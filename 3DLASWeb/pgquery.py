from fastapi import FastAPI, HTTPException, Query
import psycopg2
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List


app = FastAPI()
origins = ["http://localhost:5173", "http://localhost",
    "http://localhost:8000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="kad",
        user="postgres",
        password="PC3k261ly"
    )

@app.get("/addresses")
def get_addresses(query: Optional[str] = Query(None)):
    conn = get_db_connection()
    cur = conn.cursor()
    if query:
        # Use ILIKE for case-insensitive matching in PostgreSQL
        cur.execute("SELECT DISTINCT name FROM synth_pc WHERE name ILIKE %s ORDER BY name", (f"%{query}%",))
    else:
        cur.execute("SELECT DISTINCT name FROM synth_pc ORDER BY name")
    addresses = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return addresses

@app.get("/baunits")
def get_baunits(name: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT bau_id 
        FROM la_su_table 
        WHERE name = %s 
        ORDER BY bau_id
    """, (name,))
    baunits = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return baunits

@app.get("/spatialunits")
def get_spatialunits(name: str, bau:str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT su_id 
        FROM la_su_table 
        WHERE name = %s and bau_id = %s
        ORDER BY su_id
    """, (name,bau))
    spatialunits = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return spatialunits
@app.get("/rooms")
def get_rooms(su_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT room_id 
        FROM synth_pc 
        WHERE su_id = %s 
        ORDER BY room_id
    """, (su_id))
    rooms = [{"room_id": row[0]} for row in cur.fetchall()]
    cur.close()
    conn.close()
    return rooms
@app.get("/room-points-all")
def get_points_by_su(su_id: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            ST_X(geom_wgs), ST_Y(geom_wgs), z
        FROM (
            SELECT ST_Transform(ST_SetSRID(ST_MakePoint(x, y), 28992), 4326) AS geom_wgs, z
            FROM synth_pc WHERE su_id = %s
        ) AS transformed
    """, (su_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"x": r[0], "y": r[1], "z": r[2]} for r in rows]


def extract_date(date_str):
    return date_str.split()[0] if date_str and " " in date_str else (date_str or "")

@app.get("/building-bbox")
def get_building_bbox(name: str):
    conn = get_db_connection()
    cur = conn.cursor()

    # Step 1: Transform all x/y to WGS84 (EPSG:4326), then get bounding box
    cur.execute("""
        SELECT 
            MIN(ST_X(geom_wgs)) as min_lon,
            MIN(ST_Y(geom_wgs)) as min_lat,
            MAX(ST_X(geom_wgs)) as max_lon,
            MAX(ST_Y(geom_wgs)) as max_lat,
            MIN(z) as min_z,
            MAX(z) as max_z
        FROM (
            SELECT ST_Transform(ST_SetSRID(ST_MakePoint(x, y), 28992), 4326) AS geom_wgs, z
            FROM synth_pc
            WHERE name = %s
        ) AS transformed_points;
    """, (name,))

    row = cur.fetchone()
    cur.close()
    conn.close()

    if row and all(r is not None for r in row):
        return {
            "min_lon": row[0],
            "min_lat": row[1],
            "max_lon": row[2],
            "max_lat": row[3],
            "min_z": row[4],
            "max_z": row[5]
        }
    else:
        return {"error": "No geometry found for building"}


class SUModel(BaseModel):
    su_id: str
    label: Optional[str]
    ext_adressid: Optional[str]
    bau_id: Optional[str]
    computed_area: Optional[float]
    surfacerelation: Optional[str]

class BAUModel(BaseModel):
    bau_id: str
    la_bautype: Optional[str]
    begin_lifespan: Optional[str]
    end_lifespan: Optional[str]
    r_id: Optional[str]

class RightModel(BaseModel):
    r_id: str
    la_righttype: Optional[str]
    share: Optional[str]
    begin_lifespan: Optional[str]
    end_lifespan: Optional[str]
    p_id: Optional[str]

class PartyModel(BaseModel):
    p_id: str
    party_name: Optional[str]
    ext_id: Optional[str]

class AllData(BaseModel):
    su: SUModel
    bau: List[BAUModel]
    rights: List[RightModel]
    parties: List[PartyModel]



@app.post("/update-all")
def update_all(data: AllData):
    conn = get_db_connection()
    cur = conn.cursor()

    # ✅ Save all parties
    for party in data.parties:
        cur.execute("""
            INSERT INTO la_party_table (p_id, party_name, ext_id)
            VALUES (%s, %s, %s)
            ON CONFLICT (p_id) DO UPDATE SET
                party_name = EXCLUDED.party_name,
                ext_id = EXCLUDED.ext_id
        """, (party.p_id, party.party_name, party.ext_id))

    # ✅ Save all rights
    for right in data.rights:
        cur.execute("""
            INSERT INTO la_right_table (r_id, la_righttype, share, begin_lifespan, end_lifespan, p_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (r_id) DO UPDATE SET
                la_righttype = EXCLUDED.la_righttype,
                share = EXCLUDED.share,
                begin_lifespan = EXCLUDED.begin_lifespan,
                end_lifespan = EXCLUDED.end_lifespan,
                p_id = EXCLUDED.p_id
        """, (
            right.r_id, right.la_righttype, right.share,
            right.begin_lifespan, right.end_lifespan, right.p_id
        ))

    # ✅ Save multiple BAUs
    for bau in data.bau:
        cur.execute("SELECT id FROM la_bau_table WHERE bau_id = %s AND r_id = %s", (bau.bau_id, bau.r_id))
        row = cur.fetchone()
        if row:
            cur.execute("""
                UPDATE la_bau_table SET
                    la_bautype = %s,
                    begin_lifespan = %s,
                    end_lifespan = %s
                WHERE id = %s
            """, (
                bau.la_bautype,
                bau.begin_lifespan,
                bau.end_lifespan,
                row[0]
            ))
        else:
            cur.execute("""
                INSERT INTO la_bau_table (bau_id, r_id, la_bautype, begin_lifespan, end_lifespan)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (bau_id, r_id) DO UPDATE SET
                    la_bautype = EXCLUDED.la_bautype,
                    begin_lifespan = EXCLUDED.begin_lifespan,
                    end_lifespan = EXCLUDED.end_lifespan
            """, (
                bau.bau_id,
                bau.r_id,
                bau.la_bautype,
                bau.begin_lifespan,
                bau.end_lifespan
            ))

    # ✅ Save SU (spatial unit)
    # ✅ Corrected SU insert statement
    cur.execute("""
        INSERT INTO la_su_table (su_id, label, ext_adressid, computed_area, bau_id, surfacerelation)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (su_id) DO UPDATE SET
            label = EXCLUDED.label,
            ext_adressid = EXCLUDED.ext_adressid,
            bau_id = EXCLUDED.bau_id,
            computed_area = EXCLUDED.computed_area,
            surfacerelation = EXCLUDED.surfacerelation
    """, (
        data.su.su_id,
        data.su.label,
        data.su.ext_adressid,
        data.su.computed_area,
        data.su.bau_id,
        data.su.surfacerelation,
    ))

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Saved all linked data successfully"}

@app.get("/load-by-bau")
def load_by_bau(su_id: str = Query(...)):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # 🔹 1. Load SU
        cur.execute("SELECT * FROM la_su_table WHERE su_id = %s", (su_id,))
        su_row = cur.fetchone()
        if not su_row:
            raise HTTPException(status_code=404, detail="SU not found")
        su = dict(zip([desc[0] for desc in cur.description], su_row))
        bau_id = su["bau_id"]

        # 🔹 2. Load BAU records — all rows for this bau_id
        cur.execute("SELECT * FROM la_bau_table WHERE bau_id = %s", (bau_id,))
        bau_rows = cur.fetchall()
        bau_data = [dict(zip([desc[0] for desc in cur.description], row)) for row in bau_rows]

        # If needed: send a representative BAU record (e.g. for metadata)
        bau_summary = bau_data[0] if bau_data else {}

        # 🔹 3. Load rights linked to this BAU
        r_ids = tuple(row["r_id"] for row in bau_data if row.get("r_id"))
        rights = []
        if r_ids:
            query = "SELECT * FROM la_right_table WHERE r_id IN %s"
            cur.execute(query, (r_ids,))
            rights = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]

        # 🔹 4. Load parties for those rights
        p_ids = tuple(set(r["p_id"] for r in rights if r.get("p_id")))
        parties = []
        if p_ids:
            query = "SELECT * FROM la_party_table WHERE p_id IN %s"
            cur.execute(query, (p_ids,))
            parties = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]

        # 🔹 5. All spatial units under the same BAU
        cur.execute("SELECT * FROM la_su_table WHERE bau_id = %s", (bau_id,))
        sus = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]

        return {
            "bau": bau_summary,     # single summary object, for form display
            "bau_rows": bau_data,   # full array if you want to track all r_id links
            "rights": rights,
            "parties": parties,
            "sus": sus
        }

    finally:
        cur.close()
        conn.close()


@app.get("/search-parties")
def search_parties(query: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p_id, party_name, ext_id 
        FROM la_party_table 
        WHERE LOWER(party_name) LIKE LOWER(%s)
        ORDER BY party_name
        LIMIT 10
    """, (f"%{query}%",))
    parties = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return parties


@app.get("/next-ids")
def get_next_ids():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT MAX(CAST(SUBSTRING(p_id FROM '[0-9]+') AS INTEGER)) FROM la_party_table")
    max_pid = cur.fetchone()[0] or 0

    cur.execute("SELECT MAX(CAST(SUBSTRING(r_id FROM '[0-9]+') AS INTEGER)) FROM la_right_table")
    max_rid = cur.fetchone()[0] or 0

    cur.close()
    conn.close()
    return {
        "next_p_id": f"p_{max_pid + 1}",
        "next_r_id": f"r_{max_rid + 1}"
    }

@app.get("/linked-graph-by-party")
def get_linked_data_by_party(p_id: str):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # 1. Get all rights linked to this party
        cur.execute("SELECT * FROM la_right_table WHERE p_id = %s", (p_id,))
        rights = [dict(zip([desc[0] for desc in cur.description], r)) for r in cur.fetchall()]
        r_ids = [r["r_id"] for r in rights]

        # 2. Get all BAUs that link to these rights
        cur.execute("""
            SELECT DISTINCT * FROM la_bau_table
            WHERE r_id = ANY(%s)
        """, (r_ids,))
        baus = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
        bau_ids = list(set(row["bau_id"] for row in baus))

        # 3. Get all SUs under those BAUs
        cur.execute("SELECT * FROM la_su_table WHERE bau_id = ANY(%s)", (bau_ids,))
        sus = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]

        # 4. Load party info
        cur.execute("SELECT * FROM la_party_table WHERE p_id = %s", (p_id,))
        party = dict(zip([desc[0] for desc in cur.description], cur.fetchone()))

        return {
            "rights": rights,
            "bau_rows": baus,
            "bau": baus[0] if baus else {},
            "sus": sus,
            "parties": [party]
        }
    finally:
        cur.close()
        conn.close()


@app.get("/nearest-attribute")
def get_nearest_attribute(
    name: str,
    lon: float = Query(...),
    lat: float = Query(...),
    height: float = Query(...)
):
    adjusted_height = height - 2.0

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Find nearest point
        cur.execute("""
            SELECT x, y, z, lon, lat, room_id, su_id
            FROM (
                SELECT x, y, z, lon, lat, room_id, su_id,
                       ((lon - %s)^2 + (lat - %s)^2 + (z - %s)^2) AS dist
                FROM synth_pc
                WHERE name = %s
                ORDER BY dist ASC
                LIMIT 1
            ) AS nearest_point
        """, (lon, lat, adjusted_height, name))
        row = cur.fetchone()
        if not row:
            return {"error": "No nearby point found"}

        x, y, z, lon, lat, room_id, su_id = row

        # Load clicked SU info
        cur.execute("SELECT label, ext_adressid, computed_area, bau_id FROM la_su_table WHERE su_id = %s", (su_id,))
        su_row = cur.fetchone()
        su_info = {
            "label": su_row[0],
            "ext_adressid": su_row[1],
            "computed_area": su_row[2],
            "bau_id": su_row[3]
        } if su_row else {}

        bau_id = su_info.get("bau_id")

        # Load other SUs in the same BAU
        other_sus = []
        if bau_id:
            cur.execute("SELECT su_id, label, ext_adressid, computed_area FROM la_su_table WHERE bau_id = %s", (bau_id,))
            other_sus = [dict(zip([desc[0] for desc in cur.description], r)) for r in cur.fetchall()]

        # Load rights and parties
        cur.execute("""
            SELECT r.r_id, r.la_righttype, p.p_id, p.party_name
            FROM la_su_table su
            JOIN la_bau_table b ON su.bau_id = b.bau_id
            JOIN la_right_table r ON b.r_id = r.r_id
            JOIN la_party_table p ON r.p_id = p.p_id
            WHERE su.su_id = %s
        """, (su_id,))

        right_party_pairs = [
            {
                "r_id": r_id,
                "la_righttype": la_righttype,
                "p_id": p_id,
                "party_name": party_name
            }
            for r_id, la_righttype, p_id, party_name in cur.fetchall()
        ]

        return {
            "x": x,
            "y": y,
            "z": z,
            "lon": lon,
            "lat": lat,
            "room_id": room_id,
            "su_id": su_id,
            "su": su_info,
            "other_sus": other_sus,
            "rights": right_party_pairs
        }

    finally:
        cur.close()
        conn.close()




@app.get("/room-points-bau")
def get_points_by_bau(su_id: str):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Get the BAU for this SU
        cur.execute("SELECT bau_id FROM la_su_table WHERE su_id = %s", (su_id,))
        row = cur.fetchone()
        if not row:
            return {"error": "SU not found"}
        bau_id = row[0]

        # Get points for the clicked SU
        cur.execute("""
            SELECT ST_X(geom_wgs), ST_Y(geom_wgs), z
            FROM (
                SELECT ST_Transform(ST_SetSRID(ST_MakePoint(x, y), 28992), 4326) AS geom_wgs, z
                FROM synth_pc WHERE su_id = %s
            ) AS transformed
        """, (su_id,))
        highlighted = [{"x": r[0], "y": r[1], "z": r[2]} for r in cur.fetchall()]

        # Get points for other SUs in the same BAU (excluding clicked SU)
        cur.execute("""
            SELECT ST_X(geom_wgs), ST_Y(geom_wgs), z
            FROM (
                SELECT ST_Transform(ST_SetSRID(ST_MakePoint(x, y), 28992), 4326) AS geom_wgs, z
                FROM synth_pc 
                WHERE su_id IN (
                    SELECT su_id FROM la_su_table WHERE bau_id = %s AND su_id != %s
                )
            ) AS transformed
        """, (bau_id, su_id))
        related = [{"x": r[0], "y": r[1], "z": r[2]} for r in cur.fetchall()]

        return {"highlighted": highlighted, "related": related}

    finally:
        cur.close()
        conn.close()

@app.get("/bau-points")
def get_bau_points(bau_id: str):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Get all points for the given BAU (across all SUs)
        cur.execute("""
            SELECT ST_X(geom_wgs), ST_Y(geom_wgs), z, su_id
            FROM (
                SELECT ST_Transform(ST_SetSRID(ST_MakePoint(x, y), 28992), 4326) AS geom_wgs, z, su_id
                FROM synth_pc
                WHERE su_id IN (SELECT su_id FROM la_su_table WHERE bau_id = %s)
            ) AS transformed
        """, (bau_id,))
        rows = cur.fetchall()

        if not rows:
            return {"error": "No points found for BAU"}

        # Group points by SU
        points_by_su = {}
        for x, y, z, su_id in rows:
            if su_id not in points_by_su:
                points_by_su[su_id] = []
            points_by_su[su_id].append({"x": x, "y": y, "z": z})

        return {"points_by_su": points_by_su}

    finally:
        cur.close()
        conn.close()
@app.get("/load-by-bau-id")
def load_by_bau_id(bau_id: str = Query(...)):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # 1️⃣ Get all BAU records
        cur.execute("SELECT * FROM la_bau_table WHERE bau_id = %s", (bau_id,))
        bau_rows = cur.fetchall()
        if not bau_rows:
            raise HTTPException(status_code=404, detail="BAU not found")
        bau_data = [dict(zip([desc[0] for desc in cur.description], row)) for row in bau_rows]
        bau_summary = bau_data[0]  # First record as summary

        # 2️⃣ Get rights linked to this BAU
        r_ids = tuple(row["r_id"] for row in bau_data if row.get("r_id"))
        rights = []
        if r_ids:
            cur.execute("SELECT * FROM la_right_table WHERE r_id IN %s", (r_ids,))
            rights = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]

        # 3️⃣ Get parties linked to rights
        p_ids = tuple(set(r["p_id"] for r in rights if r.get("p_id")))
        parties = []
        if p_ids:
            cur.execute("SELECT * FROM la_party_table WHERE p_id IN %s", (p_ids,))
            parties = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]

        # 4️⃣ Get SUs under this BAU
        cur.execute("SELECT * FROM la_su_table WHERE bau_id = %s", (bau_id,))
        sus = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]

        return {
            "bau": bau_summary,
            "bau_rows": bau_data,
            "rights": rights,
            "parties": parties,
            "sus": sus
        }

    finally:
        cur.close()
        conn.close()
