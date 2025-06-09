<p align="center">
  <img src="thesismethod.drawio.png" alt="Description of the figure" width="800"/>
  <br>
</p>

# Point Cloud for 3D Land Administration System (LAS)

## Abstract:
As cities grow denser and more and more in vertical directions, Land Administration Systems (LAS) must evolve to represent complex, multi-level property ownership, particularly in apartment buildings. While Building Information Models (BIM) are commonly used for 3D representation, their availability remains limited for many buildings. This research explores the use of point clouds as an alternative means to represent 3D spatial units in LAS, focusing on the integration of cadastral floor plans and the airborne Lidar point cloud datasets (in our case \ac{AHN}.)

Three apartment cadastral drawings from different years in Rotterdam serve as case studies. The proposed methodology involves five main steps: (1) parsing the scanned image of the floor plans using image processing to extract cadastral room boundary polygons; (2) segmenting AHN point cloud (3); generating synthetic point clouds by extruding floor plan polygons and aligning them with AHN; (4) storing these 3D spatial units in a PostgreSQL-based database following the ISO 19152:2024 \ac{LADM}; and (5) developing a web-based 3D LAS using Vue.js, Cesium, and FastAPI for visualization and interaction.

Results show that unit boundaries can be extracted from cadastral drawings and converted into 3D point clouds for integration into a cadastral database. The synthetic point clouds include room-level attributes and spatial identifiers, enabling interactive visualization and \ac{LADM} information through a web interface that can be accessed by the public and stakeholders. However, challenges such as misalignment due to occlusion in \ac{AHN} data and inconsistent quality in older floor plan drawings affect the accuracy and automation of the process.

This research demonstrates that point clouds can effectively serve as final 3D representations in land administration, enabling a seamless integration with AHN that offers representation of real-world features such as building facades, walls, and fences, which often delineate cadastral boundaries. 

## Procedure:
The code is organized into two parts:
### Construct Building Point Cloud from Floor plan: 
This part can be found in [ConstructPC.ipynb](ConstructPC.ipynb), which involves the first three steps of the pipeline: 
(1) parsing the scanned image of the floor plans using image processing to extract cadastral room boundary polygons; 
(2) segmenting AHN point cloud 
(3) generating synthetic point clouds by extruding floor plan polygons and aligning them with AHN; 
### Visualize 3D LAS:
This second part is documented in [3DLASWeb](3DLASWeb)
(4) storing these 3D spatial units in a PostgreSQL-based database following the ISO 19152:2024 \ac{LADM}; and 
(5) developing a web-based 3D LAS using Vue.js, Cesium, and FastAPI for visualization and interaction.
