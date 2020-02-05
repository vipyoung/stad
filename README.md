# STAD: Spatio Temporal Adjustment of Travel Time Estimations.

This repo contains code and links to data to reproduce experiments conducted in the following paper:
- Sofiane Abbar, Rade Stanonevic, Mohamed Mokbel. STAD: Spatio-Temporal Adjustment of Traffic Agnostic Travel Time Estimates. Under submission at IEEE MDM 2020. 


# Get Started:
- First download data from this link ([porto_nyc_data](https://drive.google.com/file/d/19xed6v0L68M_aIT6N1b10qAupo5AYGTl/view?usp=sharing)), uncompress it into this folder.
- Create a python 2.7 virtual environment and install dependencies: `pip install -r requirements.txt`
- Run one of the codes (*.py) as follows: `python stad_st.py porto` 

# Data preparation for new dataset:
- First, get your trip data in the following format (see sample in data/nyc_1k.csv): `TripStartTime,PickupLon,PickupLat,DropLon,DropLat,GT_Distance,GT_Duration,OsrmDistance,OsrmDuration`
- Next, download shapefile of administrative zones from [here](https://wambachers-osm.website/boundaries/). You can use QGIS to crop/edit the shapefile. Make sure coordinate system is in WGS84.
- Now, you can run: `python trip_location_to_zone.py` to infer the zone id of each trip origin/destination location. A new file (*_zoned.csv) will be created in data/.  
