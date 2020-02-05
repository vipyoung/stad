"""
Author: Sofiane Abbar
This script maps in a very efficient way trip locations (lat,lon) into their
corresopnding zones. 
It uses an r-tree to index all zones, then runs a join query.
"""


from shapely.geometry import Point, shape, Polygon
import json
from collections import defaultdict
from rtree import index
import shapefile

# load ShapeFile file for zones
zone_file = 'data/admin_boundaries/nyc_admin/nyct2010_wgs84_truncated.shp'
#zone_file = 'data/porto_admin/porto_admin3_truncated.shp'

sf = shapefile.Reader(zone_file)
shapes = sf.shapes()


# Indexing the polygons
indx = index.Index()
polygons = []
for i, shape in enumerate(shapes):
	indx.insert(i, shape.bbox)
	polygons.append(Polygon(shape.points))

def get_zone_optimized(lonlat, zone_idx, polygons):
	point = Point(lonlat)
	for j in zone_idx.intersection(lonlat):
		if(point.within(polygons[j])):
			return j
	return -1

# load csv trip data (this data is without zones):
trip_file = 'data/nyc_1k.csv'
with open(trip_file) as f, open(trip_file.replace('.csv', '_zoned.csv'), 'w') as g:
	line = f.readline()
	g.write(line.strip('\n') + 'sourceZone,DestZone\n')
	cnt = 0
	for line in f:
		cnt+=1
		x = line.strip().split(',')
		slon, slat, dlon, dlat = map(float, x[1:5])
		s_zone = get_zone_optimized([slon, slat], indx, polygons)
		# s_zone = 49
		d_zone = get_zone_optimized([dlon, dlat], indx, polygons)
		print cnt, s_zone, d_zone
		g.write(line.strip('\n')+',%s,%s\n' % (s_zone, d_zone))

print 'Done'

