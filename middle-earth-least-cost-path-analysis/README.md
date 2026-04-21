# Least Cost Path Analysis: Frodo & Sam’s Journey to Mordor

## Project Overview
This project models the journey of Frodo and Sam to Mordor using least cost path analysis. Terrain, land cover, and environmental hazards were incorporated into a cost surface to determine the most efficient route across Middle-earth.

## Objective
To apply GIS-based least cost path analysis to simulate optimal route selection based on environmental constraints.


## Data Sources
- Digital Elevation Model (DEM)
- Land cover / terrain data
- Fictional hazard layers (e.g., enemy presence, impassable terrain)
- Study area boundary (Middle-earth extent)


## Methods

### Cost Surface Creation
- Derived slope from DEM
- Assigned higher cost to steep terrain
- Classified land cover types by travel difficulty
- Incorporated hazard zones with increased cost

### Analysis
- Combined layers into a weighted cost surface
- Defined start point (Shire) and end point (Mordor)
- Ran least cost path analysis
- Generated optimal route


## Tools Used
- ArcGIS Pro
- ArcGIS Online
- Raster analysis tools
- Cost distance / least cost path tools


## Skills Demonstrated
- Raster analysis
- Cost surface modeling
- Spatial decision modeling
- Terrain analysis
- GIS problem solving


## Results
The model identifies an optimal route minimizing travel cost based on terrain and hazards. Results highlight how environmental constraints influence movement across the landscape.

## Product Preview
[Project Homepage]
## Map Output
[Live Experience Builder](https://experience.arcgis.com/experience/91c944ebf4264621adc27c55e4557d7f/page/Page)
