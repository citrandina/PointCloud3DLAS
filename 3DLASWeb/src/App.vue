<template>
  <div id="cesiumContainer"></div>
  <div class="su_selection">
    <h3>BAUnit</h3>

    <!-- Classification Filter Checkboxes -->
<div v-for="classVal in classifications" :key="classVal" class="room-checkbox">
  <label class="custom-checkbox-container">
    <input
      type="checkbox"
      :value="classVal"
      v-model="selectedClassifications"
      @change="updateClassificationVisibility"
    />
    <span
      class="custom-checkmark"
      :style="{
        borderColor: selectedClassifications.includes(classVal)
          ? manualClassifications[classVal]?.color
          : '#ddd',
        backgroundColor: selectedClassifications.includes(classVal)
          ? manualClassifications[classVal]?.color + '33'
          : '#f8f8f8'
      }"
    >
      <svg v-if="selectedClassifications.includes(classVal)" class="checkmark-icon" viewBox="0 0 24 24">
        <path fill="none" :stroke="manualClassifications[classVal]?.color" stroke-width="3" d="M4 12l6 6L20 6"/>
      </svg>
    </span>
    <span
      class="checkbox-label"
      :style="{
        backgroundColor: selectedClassifications.includes(classVal)
          ? manualClassifications[classVal]?.color
          : '#eee',
        color: selectedClassifications.includes(classVal)
          ? '#fff'
          : '#aaa'
      }"
    >
      {{ manualClassifications[classVal]?.label || ('Class ' + classVal) }}
    </span>
  </label>
</div>



  </div>


  <div class="form_selection">
    <h2>Land Administration Information</h2>
  <!-- D3 Graph Visual -->


<!-- Select Address -->
<label>Search Address:</label>
<input v-model="searchAddressQuery" @input="searchAddress" placeholder="Type address...">

<ul v-if="addressSuggestions.length" class="suggestions-list">
  <li
    v-for="addr in addressSuggestions"
    :key="addr"
    @click="selectAddress(addr)"
  >
    {{ addr }}
  </li>
</ul>

<!-- Select SU_ID -->
<label>Select BAUnit (bau_id):</label>
<select v-model="selectedBauId" @change="fetchSuIds">
  <option v-for="bau in bauOptions" :key="bau" :value="bau">{{ bau }}</option>
</select>
    <label>Select Spatial Unit (su_id):</label>
<select v-model="selectedSuId" @change="loadLinkedData">
  <option v-for="su in suOptions" :key="su" :value="su">{{ su }}</option>
</select>

<button v-if="selectedSuId" @click="showEditor = true" class="edit-button">Edit Information</button>
<!-- Clear Selection Button -->
<button @click="clearSelection" class="edit-button clear-button" style="margin-top: 10px;">Clear Selection</button>

    <!-- Modal Toggle Button -->
<!--<button @click="showGraph = true" class="edit-button">Show Graph</button>-->


  </div>
    <div class="form_selection" v-if="showEditor">
      <h2>Edit LADM Form</h2>
      <h3>Party Information</h3>
<button @click="addParty">Add New Party</button>

 <div
  v-for="(party, index) in partyDataList"
  :key="party.p_id"
  class="edit-party-block"
>
  <h3>Party #{{ index + 1 }}</h3>

  <!-- Only show select/new toggle for newly added parties -->
  <div v-if="isNewParty[index] !== undefined">
    <label>Mode</label>
    <select v-model="isNewParty[index]">
      <option :value="true">Add New</option>
      <option :value="false">Select Existing</option>
    </select>
  </div>

  <!-- New Party Mode -->
  <div v-if="isNewParty[index] === true">
    <label>Party ID</label>
    <input v-model="party.p_id" disabled />

    <label>Party Name</label>
    <input v-model="party.party_name" />

    <label>External ID</label>
    <input v-model="party.ext_id" />
  </div>

  <!-- Select Existing Mode -->
  <div v-else-if="isNewParty[index] === false">
    <label>Search Party by Name</label>
    <input
      v-model="searchQuery[index]"
      @input="searchParties(index)"
      placeholder="Type to search..."
    />
    <ul
      v-if="partySuggestions[index]?.length"
      style="border: 1px solid #ccc; background: #fff; padding: 4px;"
    >
      <li
        v-for="suggestion in partySuggestions[index]"
        :key="suggestion.p_id"
        @click="selectParty(index, suggestion)"
        style="cursor: pointer; padding: 2px 6px;"
      >
        {{ suggestion.party_name }} ({{ suggestion.p_id }})
      </li>
    </ul>
  </div>

  <!-- Existing party (loaded from DB) -->
  <div v-else>
    <label>Party ID</label>
    <input v-model="party.p_id" disabled />

    <label>Party Name</label>
    <input v-model="party.party_name" />

    <label>External ID</label>
    <input v-model="party.ext_id" />
  </div>

  <button @click="removeParty(index)">Remove Party</button>

  <hr />
</div>


<h3>Right Information</h3>
<button @click="addRight">Add New Right</button>

        <div v-for="(right, index) in rightDataList" :key="right.r_id" class="edit-right-block">
    <h3>Right #{{ index + 1 }}</h3>
    <label>Right ID</label>
    <input v-model="right.r_id" />

    <label>Right Type</label>
    <input v-model="right.la_righttype" />

    <label>Share</label>
    <input v-model="right.share" />

    <label>Start of Right</label>
    <datepicker v-model="right.begin_lifespan" />

    <label>End of Right</label>
    <datepicker v-model="right.end_lifespan" />

    <label>Owner (Party ID)</label>
    <input v-model="right.p_id" />

    <button @click="removeRight(index)">Remove Right</button>

    <hr />
  </div>




      <br><br>
    <h3>Basic Administrative Unit Information</h3>

     <br>
    <label>BAU ID</label><input v-model="suData.bau_id" placeholder="BAU ID" />
    <br>
    <label>Type of BAU</label><input v-model="bauData.la_bautype" placeholder="Type" />
    <br>
    <label> Start of BAU Date</label><datepicker v-model="bauData.begin_lifespan" />
    <br>
    <label> End of BAU Date</label><datepicker v-model="bauData.end_lifespan" />

    <h3>Spatial Unit (SU)</h3>
      <label>SU ID</label><input v-model="suData.su_id" placeholder="SU ID" />
    <br>
    <label>Label</label><input v-model="suData.label" placeholder="Label" />
    <br>
    <label>Address</label><input v-model="suData.ext_adressid" placeholder="Address ID" />
      <br>
    <label>Label</label><input v-model="suData.computed_area" placeholder="Area" />


<!-- Hidden inputs for required IDs -->
<input type="hidden" v-model="suData.su_id" />
<input type="hidden" v-model="bauData.bau_id" />
<input type="hidden" v-model="rightData.r_id" />
<input type="hidden" v-model="partyData.p_id" />
<!-- Go Back Button -->
<button @click="showEditor = false" class="back-button">Go Back</button>

<!-- Save All Button -->
<button @click="saveAll">Save All</button>



</div>

<!-- Graph Panel -->
<div class="graph-panel-resizable" ref="resizablePanel">
  <div class="resize-handle" @mousedown="startResize"></div>
  <div class="graph-header">
  <div class="graph-title">LADM Graph</div>
  <button @click="partyFocusedData = null" class="edit-button back-button-align">
    Back to Full Graph
  </button>
</div>
  <div style="background: #f3f3f3; border-bottom: 1px solid #ccc;">

  </div>
    <!-- 👇 Add the button here -->

<LinkedGraph
    :key="graphKey"
  :linkedData="partyFocusedData
    ? {
        sus: partyFocusedData.sus,
        bau_rows: partyFocusedData.bau_rows,
        bau: partyFocusedData.bau,
        rights: partyFocusedData.rights,
        parties: partyFocusedData.parties
      }
    : {
        sus: suArray,
        bau_rows: bauRows,
        bau: bauData,
        rights: rightDataList,
        parties: partyDataList
      }"
  :highlightedSuId="selectedSuId"
  :highlightedBauId="selectedBauId"
  @su-clicked="onSuClicked"
  @party-clicked="onPartyClicked"
  @bau-clicked="onBauClicked"
/>




</div>



  <!-- Toggle underground mode -->
  <div class="underground-toggle">
    <label class="switch-label">
      <h5>Underground</h5>
      <label class="switch">
        <input
          type="checkbox"
          v-model="showUnderground"
          @change="toggleUnderground"
        />
        <span class="slider round"></span>
      </label>
    </label>
  </div>
<div v-if="showTooltip"
     :style="{
       position: 'absolute',
       top: hoverPosition.y + 'px',
       left: hoverPosition.x + 'px',
       background: '#fff',
       border: '1px solid #ccc',
       padding: '6px 10px',
       fontSize: '13px',
       zIndex: 999,
       borderRadius: '4px',
       maxWidth: '280px'
     }">
  <div v-if="clickedCoordinates">
    <strong>Clicked Coordinates:</strong><br>
    Lon: {{ clickedCoordinates.lon.toFixed(2) }}
    Lat: {{ clickedCoordinates.lat.toFixed(2) }}
    Z: {{ clickedCoordinates.height.toFixed(2) }}
  </div>
  <hr>
  <div v-if="hoveredSUData.sus.length">
  <strong>Spatial Units (SU):</strong>
  <ul style="padding-left: 14px; margin: 4px 0;">
    <li v-for="su in hoveredSUData.sus" :key="su.su_id"
        :style="{
          fontWeight: su.su_id === hoveredSUData.clicked_su_id ? 'bold' : 'normal',
          color: su.su_id === hoveredSUData.clicked_su_id ? '#2b2929' : '#333'
        }">
      {{ su.label || 'N/A' }}
    </li>
  </ul>
</div>


<div v-if="hoveredRights.length">
  <hr>
  <strong>Rights & Parties:</strong>
  <ul style="padding-left: 14px; margin: 4px 0;">
    <li v-for="(r, index) in hoveredRights" :key="index">
      <span style="font-weight: 600;">{{ r.party_name }}</span> ({{ r.la_righttype }})
    </li>
  </ul>
</div>



  </div>



</template>

<script lang="ts">
interface PartyData {
  p_id: string;
  party_name: string;
  ext_id: string;
}
interface RightData {
  p_id: string;
  r_id: string;
  la_righttype: string;
  share: string;
  begin_lifespan: Date | undefined;
  end_lifespan: Date | undefined;
}
interface BauData{
  bau_id: string;
  r_id: string;
  la_bautype: string;
  begin_lifespan: Date | undefined;
  end_lifespan: Date | undefined;
}
interface SuData{
  bau_id: string;
  su_id: string;
  label: string;
  ext_adressid: string;
  computed_area: number;
  surfacerelation: number;
}
interface LinkedData {
  parties: PartyData[];
  rights: RightData[];
  sus: SuData[];
  bau_rows: BauData[];
  bau: BauData; // 👈 summary object (e.g., first row)
}






	import { defineComponent, ref } from 'vue'
  import {
    Viewer,
    Color,
    Ion,
    OpenStreetMapImageryProvider,
    HeightReference,
    ImageryLayer,
    CesiumTerrainProvider,
    Cartesian3,
    ScreenSpaceEventType,
    NearFarScalar, Model, IonResource
  } from "cesium";

	import { Cesium3DTileset } from 'cesium';
	import { Transforms } from 'cesium';
	import { Matrix4 } from 'cesium';
	import { HeadingPitchRange } from 'cesium';
	import { HeadingPitchRoll } from 'cesium';
	import { Terrain } from 'cesium';
  import { Math as cMath} from 'cesium';
	import { Cartographic, Rectangle, BoundingSphere } from 'cesium';
	import { ScreenSpaceEventHandler, Cartesian2, Cesium3DTileStyle, PointPrimitiveCollection, Cesium3DTileFeature} from 'cesium';
  import Datepicker from 'vue3-datepicker'
  import LinkedGraph from './components/LinkedGraph.vue';
  import { nextTick } from 'vue';
	import "cesium/Build/Cesium/Widgets/widgets.css";
  import * as Cesium from "cesium";

	Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJkNjZjNjlmNS1iMTFiLTQ0NTAtOGFhNC0xMDU4ZWJkYzc1YTAiLCJpZCI6MjgwMDIxLCJpYXQiOjE3NDA3NTU4MDd9.8dxG2HhKuKPAbxgp1MS-78h6I9f6Wpe1-ccucmOZMcA'

	declare global {
		interface Window { CESIUM_BASE_URL: string; }
	}

	window.CESIUM_BASE_URL = 'static/cesium';


  export default {
    components: {
      Datepicker,
      LinkedGraph
    },
    data() {
      return {
        graphKey: 0,
        viewer: null as Viewer | null,
        assetMap: {

          kad1: 3354392,
          kad3: 3399239,
          kad5: 3354390
        } as { [key: string]: number },
        selectedAddress: null as string | null,
        loadedTilesets: {} as Record<string, Cesium3DTileset>,
        classificationColors: {} as Record<number, string>,
        classifications: [] as number[],
        selectedClassifications: [] as number[],
        showUnderground: false,
        showEditor: false,
        isNewParty: [] as boolean[],
        searchQuery: [] as string[],
        partySuggestions: [] as any[][],
        partyFocusedData: null as LinkedData | null,
        hoveredSUData: {
        clicked_su_id: null,
        sus: [] as Array<{ su_id: string; label: string; ext_adressid: string; computed_area: number, surfacerelation: number }>
      },


        selectedBauId: null as string | null,
        selectedSuId: null as string | null,
        addressOptions: [],
        suOptions: [],
        bauOptions: [],
        suData: {} as SuData,
        bauData: {} as BauData,
        rightData: {} as RightData,
        partyData: {} as PartyData,
        suArray: [] as any[],
        showGraph: false,
        rightDataList: [] as RightData[],
        partyDataList: [] as PartyData[],
        bauRows: [],
        manualClassifications: {
          255: { label: 'Unclassified', color: '#4a505a' },
        0: { label: 'Building Envelope', color: '#838887' },
        1: { label: 'Unit 1', color: '#A3CBF1' },
        2: { label: 'Unit 2', color: '#b8e0d4' },
        3: { label: 'Unit 3', color: '#cac7ff' },
        4: { label: 'Unit 4', color: '#ea8f98' },
        5: { label: 'Unit 5', color: '#856fab' },
        6: { label: 'Unit 6', color: '#ffd1d4' },
        7: { label: 'Unit 7', color: '#deae9f' },
        8: { label: 'Unit 8', color: '#adc178' },
        9: { label: 'Unit 9', color: '#f6dca1' },
        10: { label: 'Unit 10', color: '#F5A352' },
        11: { label: 'Unit 11', color: '#79BFA1' },
        12: { label: 'Unit 12', color: '#bc5090' },
        },
            hoveredClassification: null as number | null,
        hoverPosition: { x: 0, y: 0 },

        hoveredAttribute: "Loading..." as string | null, // default or fallback message
        showTooltip: false,
        clickedCoordinates: null as { lon: number; lat: number; height: number } | null,
        highlightedSuPoints: null as Cesium.PointPrimitiveCollection | null,
        relatedSuPoints: null as Cesium.PointPrimitiveCollection | null,
        isResizing: false,
        hoveredRights: [] as Array<{ r_id: string; la_righttype: string; p_id: string; party_name: string }>,
        highlightedBauId: null as string | null,
        searchAddressQuery: "",
        addressSuggestions: [] as string[],




      };
    },



    methods: {
      async searchAddress() {
  if (!this.searchAddressQuery.trim()) {
    this.addressSuggestions = [];
    return;
  }
  const res = await fetch(`http://localhost:8000/addresses?query=${encodeURIComponent(this.searchAddressQuery)}`);
  if (res.ok) {
    this.addressSuggestions = await res.json();
  } else {
    console.error("Error fetching address suggestions");
    this.addressSuggestions = [];
  }
},

async selectAddress(addr: string) {
  this.selectedAddress = addr;
  this.addressSuggestions = [];
  this.searchAddressQuery = addr;
  await this.onAddressSelected();
  await this.fetchBauIds();
},


      async onAddressSelected() {
        if (!this.selectedAddress) return;

        const assetId = this.assetMap[this.selectedAddress];
        if (!assetId) return;

        if (this.loadedTilesets[this.selectedAddress]) {
          this.viewer?.scene.primitives.remove(this.loadedTilesets[this.selectedAddress]);
        }

        const tileset = await Cesium3DTileset.fromIonAssetId(assetId, { show: true });
        await (tileset as any).readyPromise;

        this.loadedTilesets[this.selectedAddress] = tileset;
        this.viewer?.scene.primitives.add(tileset);
        await this.viewer?.zoomTo(tileset);

        this.applyPointCloudClassificationColors(tileset); // 👈 use coloring + setup checkboxes

      },




updateClassificationVisibility() {
  const tileset = this.loadedTilesets[this.selectedAddress!];
  if (!tileset) return;

  const allowed = this.selectedClassifications;

  const colorConditions = allowed.map(classVal => [
    `\${Classification} === ${classVal}`, this.classificationColors[classVal]
  ]);
  colorConditions.push(["true", "color('#FAF7F1')"]);  // Dim gray



  const sizeConditions = allowed.map(classVal => [
    `\${Classification} === ${classVal}`, "3.0"
  ]);
  sizeConditions.push(["true", "1.0"]); // minimize others

  tileset.style = new Cesium3DTileStyle({
    color: { conditions: colorConditions },
    pointSize: { conditions: sizeConditions }
  });

  tileset.pointCloudShading = new Cesium.PointCloudShading({
    attenuation: true
  }); //Activates perspective-based point scaling

  tileset.show = true;
},


 applyPointCloudClassificationColors(tileset: Cesium3DTileset) {
  const classificationColors: Record<number, string> = {};
  const classifications: number[] = [];

  for (const [key, { color }] of Object.entries(this.manualClassifications)) {
    const classVal = Number(key);
    classifications.push(classVal);
    classificationColors[classVal] = `color('${color}')`;
  }

  this.classifications = classifications;
  this.classificationColors = classificationColors;
  this.selectedClassifications = [...classifications];

  this.updateClassificationVisibility();
},
highlightSuPoints(highlightedPoints: { x: number; y: number; z: number }[], relatedPoints: { x: number; y: number; z: number }[]) {
  if (!this.viewer) return;

  // Remove previous highlights
  if (this.highlightedSuPoints) {
    this.viewer.scene.primitives.remove(this.highlightedSuPoints);
    this.highlightedSuPoints = null;
  }
  if (this.relatedSuPoints) {
    this.viewer.scene.primitives.remove(this.relatedSuPoints);
    this.relatedSuPoints = null;
  }

  // Add highlighted SU points (red)
  const highlightedCollection = new Cesium.PointPrimitiveCollection();
  highlightedPoints.forEach(pt => {
    highlightedCollection.add({
      position: Cesium.Cartesian3.fromDegrees(pt.x, pt.y, pt.z + 43.5),
      color: Cesium.Color.RED.withAlpha(0.5),
      pixelSize: 2,
      disableDepthTestDistance: Number.POSITIVE_INFINITY,
    });
  });
  this.viewer.scene.primitives.add(highlightedCollection);
  this.highlightedSuPoints = highlightedCollection;

  // Add related SU points (dimmed)
  const relatedCollection = new Cesium.PointPrimitiveCollection();
  relatedPoints.forEach(pt => {
    relatedCollection.add({
      position: Cesium.Cartesian3.fromDegrees(pt.x, pt.y, pt.z + 43.5),
      color: Cesium.Color.SALMON.withAlpha(0.1),
      pixelSize: 3,
      disableDepthTestDistance: Number.POSITIVE_INFINITY,
    });
  });
  this.viewer.scene.primitives.add(relatedCollection);
  this.relatedSuPoints = relatedCollection;

  // Optional: Fly to the highlighted points
  const positions = highlightedPoints.map(pt => Cesium.Cartesian3.fromDegrees(pt.x, pt.y, pt.z + 43.5));
  if (positions.length > 0) {
    const boundingSphere = Cesium.BoundingSphere.fromPoints(positions);
    this.viewer.camera.flyToBoundingSphere(boundingSphere, {
      duration: 2,
      offset: new Cesium.HeadingPitchRange(
        Cesium.Math.toRadians(0),
        Cesium.Math.toRadians(-45),
        boundingSphere.radius * 2
      )
    });
  }
},





    toggleUnderground() {
      if (!this.viewer) return;

      const globe = this.viewer.scene.globe;


      // Enable or disable translucency
      globe.translucency.enabled = this.showUnderground;

      // Optional: make terrain fade in with distance
      globe.translucency.frontFaceAlphaByDistance = this.showUnderground
        ? new NearFarScalar(100.0, 0.2, 300.0, 1.0)
        : new NearFarScalar(1.0, 1.0, 1.0, 1.0);

      // Optional: let camera go underground too
      this.viewer.scene.screenSpaceCameraController.enableCollisionDetection = !this.showUnderground;
      console.log("Underground enabled:", this.showUnderground);
    },
    colorFromStyle(styleStr: string): string {
      if (!styleStr) return 'gray';
      const match = styleStr.match(/color\(['"]?(.*?)['"]?\)/);
      return match ? match[1] : 'gray';
    },

      async fetchBauIds() {
  const res = await fetch(`http://localhost:8000/baunits?name=${this.selectedAddress}`);
  this.bauOptions = await res.json();
},
      async fetchSuIds() {
  const res = await fetch(`http://localhost:8000/spatialunits?name=${this.selectedAddress}&bau=${this.selectedBauId}`);
    // Auto-load the graph for selected BAUnit
  await this.loadLinkedGraphByBau(this.selectedBauId);
  this.suOptions = await res.json();
},
parseDateFields(obj: any, fields: string[]) {
  for (const field of fields) {
    if (obj[field]) {
      obj[field] = new Date(obj[field]);
    }
  }
},


async loadLinkedData() {
  try {
    if (!this.selectedBauId) {
      throw new Error("No BAU ID selected");
    }

    // Try BAU first
    const res = await fetch(`http://localhost:8000/load-by-bau-id?bau_id=${this.selectedBauId}`);
    if (!res.ok) {
      throw new Error("BAU not found");
    }

    const data = await res.json();

    // ✅ Populate from BAU
    this.bauData = data.bau;
    this.bauRows = data.bau_rows;
    this.rightDataList = data.rights;
    this.partyDataList = data.parties;
    this.suArray = data.sus;

    this.isNewParty = this.partyDataList.map(() => undefined);
    this.searchQuery = this.partyDataList.map(() => '');
    this.partySuggestions = this.partyDataList.map(() => []);

    if (!this.selectedSuId && this.suArray.length > 0) {
      this.selectedSuId = this.suArray[0].su_id;
    }

    const selected = this.suArray.find(su => su.su_id === this.selectedSuId);
    this.suData = selected || {};

    this.parseDateFields(this.bauData, ['begin_lifespan', 'end_lifespan']);
    this.rightDataList.forEach(right =>
      this.parseDateFields(right, ['begin_lifespan', 'end_lifespan'])
    );

    this.partyFocusedData = data; // ✅ Feed into diagram

    const pointres = await fetch(`http://localhost:8000/room-points-bau?su_id=${this.selectedSuId}`);
    const { highlighted, related } = await pointres.json();
    this.highlightSuPoints(highlighted, related);

    this.showEditor = false;

  } catch (error) {
    console.warn("Fallback to SU selection:", error);

    if (!this.selectedSuId) {
      alert("No BAU found. Please select a Spatial Unit (SU) to continue.");
      return;
    }

    const res = await fetch(`http://localhost:8000/load-by-bau?su_id=${this.selectedSuId}`);
    if (!res.ok) {
      console.error("Error fetching fallback SU data");
      return;
    }

    const data = await res.json();

    this.bauData = data.bau;
    this.bauRows = data.bau_rows;
    this.rightDataList = data.rights;
    this.partyDataList = data.parties;
    this.suArray = data.sus;

    this.isNewParty = this.partyDataList.map(() => undefined);
    this.searchQuery = this.partyDataList.map(() => '');
    this.partySuggestions = this.partyDataList.map(() => []);

    const selected = this.suArray.find(su => su.su_id === this.selectedSuId);
    this.suData = selected || {};

    this.parseDateFields(this.bauData, ['begin_lifespan', 'end_lifespan']);
    this.rightDataList.forEach(right =>
      this.parseDateFields(right, ['begin_lifespan', 'end_lifespan'])
    );

    this.partyFocusedData = data; // ✅ Feed fallback into diagram

    const pointres = await fetch(`http://localhost:8000/room-points-bau?su_id=${this.selectedSuId}`);
    const { highlighted, related } = await pointres.json();
    this.highlightSuPoints(highlighted, related);

    this.showEditor = false;
  }
},


async addRight() {
  const res = await fetch('http://localhost:8000/next-ids');
  const ids = await res.json();
  this.rightDataList.push({
    r_id: ids.next_r_id,
    la_righttype: '',
    share: '',
    begin_lifespan: undefined,
    end_lifespan: undefined,
    p_id: ''
  });
},

removeRight(index: number) {
  this.rightDataList.splice(index, 1);
},

async addParty() {
  const res = await fetch('http://localhost:8000/next-ids');
  const ids = await res.json();
  this.partyDataList.push({
    p_id: ids.next_p_id,
    party_name: "",
    ext_id: "",
  });

  this.isNewParty.push(true);
  this.searchQuery.push('');
  this.partySuggestions.push([]);
},
      async searchParties(index: number) {
  if (!this.searchQuery[index]) return;
  const res = await fetch(`http://localhost:8000/search-parties?query=${this.searchQuery[index]}`);
  this.partySuggestions[index] = await res.json();
},

selectParty(index: number, suggestion: any) {
  this.partyDataList[index] = {
    p_id: suggestion.p_id,
    party_name: suggestion.party_name,
    ext_id: suggestion.ext_id
  };
  this.searchQuery[index] = suggestion.party_name;
  this.partySuggestions[index] = [];
},


removeParty(index: number) {
  this.partyDataList.splice(index, 1);
},

      async onSuClicked(suId: string) {
        this.selectedSuId = suId;
const res = await fetch(`http://localhost:8000/room-points-bau?su_id=${this.selectedSuId}`);
const { highlighted, related } = await res.json();
this.highlightSuPoints(highlighted, related);

},



async saveAll() {
  const formatted = (obj: any) => {
    const result: Record<string, any> = {};
    for (const [k, v] of Object.entries(obj)) {
      result[k] = v instanceof Date ? v.toISOString().split("T")[0] : v;
    }
    return result;
  };

  const payload = {
    su: {
      su_id: this.selectedSuId,
      ...formatted(this.suData)
    },
    bau: this.rightDataList
      .filter(r => r.r_id)
      .map(r => {
        const matchedBau = this.bauRows.find(b => b.r_id === r.r_id);
        return {
          bau_id: this.suData.bau_id,
          r_id: r.r_id,
          la_bautype: matchedBau?.la_bautype || this.bauData.la_bautype || '',
          begin_lifespan: matchedBau?.begin_lifespan || this.bauData.begin_lifespan || '',
          end_lifespan: matchedBau?.end_lifespan || this.bauData.end_lifespan || ''
        };
      }),

    rights: this.rightDataList.filter(r => r.r_id).map(formatted),
    parties: this.partyDataList.filter(p => p.p_id).map(formatted),

  };

  console.log("Sending final payload:", payload);
  if (!this.suData.bau_id && this.selectedBauId) {
  this.suData.bau_id = this.selectedBauId;
}


  const res = await fetch("http://localhost:8000/update-all", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const error = await res.text();
    console.error("Update failed:", error);
    alert("Save failed");
  } else {
    alert("Saved!");
  }
},
onMouseClick(click: { position: Cartesian2 }) {
  if (!this.viewer) return;

  const scene = this.viewer.scene;
  const cartesian = scene.pickPosition(click.position);

  this.hoveredClassification = null;
  this.hoveredAttribute = null;
  this.clickedCoordinates = null;
  this.showTooltip = false;

  if (!Cesium.defined(cartesian)) {
    console.log("pickPosition returned undefined");
    return;
  }

  const cartographic = Cesium.Cartographic.fromCartesian(cartesian);
  const lon = Cesium.Math.toDegrees(cartographic.longitude);
  const lat = Cesium.Math.toDegrees(cartographic.latitude);
  const height = cartographic.height - 43;


  this.hoverPosition = { x: click.position.x + 10, y: click.position.y + 10 };
  this.clickedCoordinates = { lon, lat, height };
  this.showTooltip = true;

  const picked = scene.pick(click.position);
  const hasProperty = picked && typeof picked.getProperty === "function";
  const classVal = hasProperty ? picked.getProperty("Classification") : null;

  if (classVal !== null && classVal !== undefined) {
    this.hoveredClassification = classVal;
    this.hoveredAttribute = `Classification: ${classVal}`;
  } else {
    const name = this.selectedAddress;
    fetch(`http://localhost:8000/nearest-attribute?name=${name}&lon=${lon}&lat=${lat}&height=${height}`)
      .then((res) => {
        if (!res.ok) throw new Error("Response not OK");
        return res.json();
      })
      .then(async (data) => {
        if (data && data.su_id && data.room_id) {
          this.suOptions = (data.other_sus || []).map(su => su.su_id);
          if (!this.suOptions.includes(data.su_id)) {
            this.suOptions.unshift(data.su_id);
          }
          this.selectedSuId = data.su_id;
          await nextTick();
          await this.loadLinkedData();
          this.hoveredSUData = {
            clicked_su_id: data.su_id,
            sus: data.other_sus || []
          };
          this.hoveredRights = data.rights || [];


          // 🔸 Also fetch and highlight the entire SU

          const res = await fetch(`http://localhost:8000/room-points-bau?su_id=${data.su_id}`);
          const { highlighted, related } = await res.json();
          this.highlightSuPoints(highlighted, related);

        } else {
          this.hoveredSUData = { clicked_su_id: null, sus: [] };
          this.hoveredRights = [];

        }
      })
      .catch((err) => {
        console.error("Error fetching attribute info:", err);
        this.hoveredAttribute = "Failed to fetch attribute";
      });

  }
},


          startResize(e) {
      this.isResizing = true;
      document.addEventListener("mousemove", this.resizePanel);
      document.addEventListener("mouseup", this.stopResize);
    },

    resizePanel(e) {
      if (!this.isResizing) return;
      const panel = document.querySelector(".graph-panel-resizable");
      const newHeight = window.innerHeight - e.clientY;
      panel.style.height = newHeight + "px";
    },

    stopResize() {
      this.isResizing = false;
      document.removeEventListener("mousemove", this.resizePanel);
      document.removeEventListener("mouseup", this.stopResize);
    },
    async onPartyClicked(partyId: string) {
      const res = await fetch(`http://localhost:8000/linked-graph-by-party?p_id=${partyId}`);
      const data = await res.json();

      this.partyFocusedData = data;   // new linked subset
      this.showGraph = true;
      // 🔸 Brief highlight for 2 seconds
      this.selectedSuId = null;
      this.selectedBauId = null;
      this.$nextTick(() => {
        const svg = document.querySelector("#graphContainer svg");
        if (svg) {
          svg.classList.add("flash-party");
          setTimeout(() => svg.classList.remove("flash-party"), 2000);
        }
      });
    },
async onBauClicked(bauId: string) {
  const address = bauId.split('_')[0]; // Extract from bauId
  this.selectedAddress = address;
  this.selectedBauId = bauId;
  this.selectedSuId = null;

  await this.onAddressSelected(); // Load tileset for new address
  await this.fetchBauIds();
  await this.fetchSuIds();

  this.partyFocusedData = null; // Reset graph subset if any
  this.highlightedBauId = bauId; // Will pass down to LinkedGraph

  const res = await fetch(`http://localhost:8000/bau-points?bau_id=${bauId}`);
  const { points_by_su } = await res.json();
  const allPoints = Object.values(points_by_su).flat();
  this.highlightSuPoints(allPoints, []);
},
      async loadLinkedGraphByBau(bauId: string) {
  const res = await fetch(`http://localhost:8000/load-by-bau-id?bau_id=${bauId}`);
  const data = await res.json();
  this.partyFocusedData = data;  // This feeds into the LinkedGraph component
  this.selectedBauId = bauId;    // Set for highlighting the node
},
clearSelection() {
  // Reset selections, but keep address so it reloads properly
  this.selectedBauId = null;
  this.selectedSuId = null;

  this.bauOptions = [];
  this.suOptions = [];

  this.bauData = {} as BauData;
  this.suData = {} as SuData;
  this.rightDataList = [];
  this.partyDataList = [];
  this.suArray = [];
  this.partyFocusedData = null;
  this.hoveredSUData = { clicked_su_id: null, sus: [] };
  this.hoveredRights = [];
  this.showEditor = false;
  this.showTooltip = false;
  this.clickedCoordinates = null;


  // 🔸 Reload BAUs based on current address
  if (this.selectedAddress) {
    this.fetchBauIds();
  }

  // 🔸 Remove Cesium highlights
  if (this.viewer) {
    if (this.highlightedSuPoints) {
      this.viewer.scene.primitives.remove(this.highlightedSuPoints);
      this.highlightedSuPoints = null;
    }
    if (this.relatedSuPoints) {
      this.viewer.scene.primitives.remove(this.relatedSuPoints);
      this.relatedSuPoints = null;
    }
  }

  this.graphKey++;
},










    },

    async mounted() {
      // Create an OpenStreetMap base layer
      let baseLayer = new ImageryLayer(new OpenStreetMapImageryProvider({
        url: "https://tile.openstreetmap.org/"
      }), {});

      // Initialize Cesium Viewer with terrain and base layer
      let viewer = new Viewer("cesiumContainer", {
        baseLayer: baseLayer,
        terrain: Terrain.fromWorldTerrain(),
      });

      this.viewer = viewer; // Store the viewer instance
      const handler = new Cesium.ScreenSpaceEventHandler(this.viewer.scene.canvas);
      handler.setInputAction(this.onMouseClick, Cesium.ScreenSpaceEventType.LEFT_CLICK);


        try {
    const res = await fetch("http://localhost:8000/addresses");
    this.addressOptions = await res.json();
  } catch (err) {
    console.error("Failed to load addresses:", err);
  }


      try {
        const ahn = [3398897];
        for (const id of ahn) {
          const tileset_ahn = await Cesium3DTileset.fromIonAssetId(id, {
            show: true // Optional: make each tileset visible
          });

          this.viewer.scene.primitives.add(tileset_ahn);
          tileset_ahn.style = new Cesium3DTileStyle({
            pointSize: 5.0  // Adjust this value to increase/decrease point size
          });
        }
      }
      catch (error) {
        console.error(`Error loading tileset: ${error}`);
      }



    },
}
</script>

<style>
html,
body,
	#cesiumContainer, #app {
		width: 100%;
		height: 100%;
		margin: 0;
		padding: 0;
		overflow: hidden;
    font-family: Helvetica;

	}


.su_selection {
    position: absolute;
    top: 80px;
    right: 30px;
    background: #d9dbdc;
    padding: 1px;
    border-radius: 5px;
    max-height: 100%;
    overflow-y: auto;
    font-size: 15px;
    z-index: 100;
    font-family: Helvetica;
}
.su_selection h3 {
  margin-top: 8px;
  margin-bottom: 5px;
  font-size: 20px;
  color: #686667;
  text-align: center;
}
.edit-button {
  margin-top: 10px;
  padding: 8px 14px;
  background-color: #686667;
  color: white;
  border: none;
  border-radius: 5px;
  font-weight: bold;
  cursor: pointer;
}
.edit-button:hover {
  background-color: #808081;
}

.form_selection {
  position: absolute;
  top: 30px;
  left: 30px;
  background: #d9dbdc;
  padding: 10px;
  border-radius: 8px;
  max-height: 60%;
  overflow-y: auto;
  font-size: 14px;
  font-family: Helvetica;
  z-index: 100;
  width: 200px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}
.form_selection h2 {
  margin-top: 2px;
  margin-bottom: 10px;
  font-size: 18px;
  color: #686667;
  text-align: center;
}
.form_selection h3 {
  margin-top: 2px;
  margin-bottom: 10px;
  font-size: 14px;
  color: #686667;
}


.form_selection label {
  font-weight: 600;
  margin-bottom: 4px;
  display: block;
  color: #41474c;
}

.form_selection input,
.form_selection select {
  width: 100%;
  padding: 6px 8px;
  margin-bottom: 12px;
  border: 1px solid #bbb;
  border-radius: 4px;
  box-sizing: border-box;
}

.form_selection datepicker {
  width: 100%;
  margin-bottom: 12px;
}

.form_selection button {
  width: 100%;
  background-color: #686667;
  color: white;
  border: none;
  padding: 10px;
  border-radius: 6px;
  font-weight: bold;
  margin-top: 20px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.form_selection button:hover {
  background-color: #8d8e8f;
}
.edit-button.clear-button {
  background-color: #686667;
  color: white;
}


.room-checkbox {
  margin-bottom: 4px;
}

.custom-checkbox-container {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 14px;
  user-select: none;
}

.custom-checkbox-container input {
  display: none; /* hide default checkbox */
}

.custom-checkmark {
  width: 16px;
  height: 16px;
  border-radius: 5px;

  position: relative;
  margin-left: 3px;
  margin-right: 5px;
  transition: background-color 0.2s ease;
  background-color: #ccc; /* default unchecked color */
}

.custom-checkbox-container input:checked + .custom-checkmark {
  opacity: 0.9;
}

.custom-checkmark .checkmark-icon {
  width: 100%;
  height: 100%;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.custom-checkbox-container input:checked + .custom-checkmark .checkmark-icon {
  opacity: 1;
}

.checkbox-label {
  padding: 3px 15px;
  border-radius: 8px;
  color: white;
  flex-grow: 1;
  text-align: center;
  transition: background-color 0.2s ease;
}

.custom-checkbox-container input:checked ~ .checkbox-label {
  background-color: inherit; /* same as the checkmark's background */
  opacity: 0.9;
}

.custom-checkbox-container input:not(:checked) ~ .checkbox-label {
  background-color: #ddd; /* default unselected background */
  color: #555;
}


.underground-toggle {
  position: absolute;
  bottom: 50px;
  right: 30px;
  z-index: 100;
  font-size: 14px;
  font-family: Helvetica;
  background: #d9dbdc;
  color: #686667;
  padding: 1px 4px;
  height: 4%;
  border-radius: 2px;
  display: flex;
  align-items: center;
  gap: 2px;
  pointer-events: auto;
}

.switch-label {
  display: flex;
  align-items: center;
  gap: 6px;
}

.switch {
  position: relative;
  display: inline-block;
  width: 40px;
  height: 20px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: 0.3s;
  border-radius: 34px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 4px;
  bottom: 3px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
}
.color-chip {
  display: inline-block;
  width: 12px;
  height: 12px;
  margin-right: 6px;
  vertical-align: middle;
  border-radius: 2px;
}

input:checked + .slider {
  background-color: #a6a4a4;
}

input:checked + .slider:before {
  transform: translateX(18px);
}
.editor-form {
  position: absolute;
  top: 20px;
  left: 30px;
  background: #eef6fb;
  padding: 15px;
  border-radius: 8px;
  max-height: 90%;
  overflow-y: auto;
  width: 400px;
  font-family: Helvetica;
  font-size: 14px;
}
.editor-form h3 {
  margin-top: 20px;
  color: #a28084;
}
.editor-form input {
  width: 100%;
  margin: 4px 0;
  padding: 5px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.editor-form select {
  width: 100%;
  padding: 5px;
  margin-bottom: 10px;
}
.editor-form button {
  background-color: #a28084;
  color: white;
  border: none;
  padding: 10px;
  width: 100%;
  border-radius: 5px;
  margin-top: 20px;
}
.back-button {
  background-color: #999;
  color: white;
  border: none;
  padding: 10px;
  width: 100%;
  border-radius: 6px;
  font-weight: bold;
  margin-top: 10px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.back-button:hover {
  background-color: #777;
}


.graph-panel-resizable {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 300px; /* default */
  background: #fff;
  border-top: 2px solid #aaa;
  z-index: 100;
  padding: 10px 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  resize: vertical; /* fallback for browsers that support it */
}

.resize-handle {
  height: 8px;
  background: #888;
  cursor: row-resize;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 101; /* make sure it's above everything inside the panel */
}



.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.modal-content {
  background: white;
  padding: 20px;
  width: 80%;
  max-width: 1000px;
  max-height: 80vh;
  overflow-y: auto;
  border-radius: 10px;
  position: relative;
  box-shadow: 0 0 15px rgba(0,0,0,0.3);
}

.close-button {
  position: absolute;
  top: 10px;
  right: 14px;
  font-size: 24px;
  border: none;
  background: none;
  cursor: pointer;
}

.graph-header {
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  background: #f3f3f3;
  border-bottom: 1px solid #ccc;
}

.graph-title {
  font-size: 20px;
  font-weight: bold;
  color: #686667;
}

.back-button-align {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
}
.flash-party .highlighted rect {
  stroke: #35e495;
  stroke-width: 3;
}

.suggestions-list {
  border: 1px solid #ccc;
  background: white;
  list-style: none;
  padding: 4px;
  max-height: 150px;
  overflow-y: auto;
  margin-top: 4px;
}
.suggestions-list li {
  padding: 4px 8px;
  cursor: pointer;
}
.suggestions-list li:hover {
  background-color: #f0f0f0;
}


</style>
