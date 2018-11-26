# -*- coding: utf-8 -*-
"""
Merges Helsinki Region street networks together (divided into 3 different datasets).

Last updated:
    28.4.2018

Author: 
    Henrikki Tenkanen
"""
import geopandas as gpd
import os
from shapely import ops
from shapely import prepared


# Buffer around (in meters)
buffer_distance = 5000

# Filepaths
grid_fp = r"C:\HY-DATA\HENTENKA\KOODIT\Opetus\Automating-GIS-processes\2017\data\TravelTimes_to_5975375_RailwayStation.shp"
links = "DR_LINKKI_K.shp"
signals = "DR_LIIKENNEVALO.shp"
limits = "DR_NOPEUSRAJOITUS_K.shp"

outdir = r"C:\HY-DATA\HENTENKA\KOODIT\Matrix2018\Digiroad\MERGED"
filenames = [links, limits, signals]
folders = [r"C:\HY-DATA\HENTENKA\KOODIT\Matrix2018\Digiroad\UUSIMAA_1", 
           r"C:\HY-DATA\HENTENKA\KOODIT\Matrix2018\Digiroad\UUSIMAA_2",
           r"C:\HY-DATA\HENTENKA\KOODIT\Matrix2018\Digiroad\ITA-UUSIMAA"]

grid = gpd.read_file(grid_fp)

# Assign flag for all geometries
grid['flag'] = 1

# Dissolve grid into a single Polygon
dissolved = grid.dissolve(by='flag')

# Create a buffer around the area
buffer = gpd.GeoDataFrame(dissolved.buffer(buffer_distance)).reset_index()
buffer.columns = ['flag', 'geometry']

# Make prepared geometry
prep_geom = prepared.prep(buffer['geometry'].values[0])

for fname in filenames:
    print(fname)
    digi_fp1 = os.path.join(folders[0], fname)
    digi_fp2 = os.path.join(folders[1], fname)
    digi_fp3 = os.path.join(folders[2], fname)
    outfp = os.path.join(outdir, "%s_Helsinki_Region.shp" % fname.replace('.shp', ''))

    # Read files
    d1 = gpd.read_file(digi_fp1)
    d2 = gpd.read_file(digi_fp2)
    d3 = gpd.read_file(digi_fp3)

    # Merge street datasets together
    data = d1.append(d2)
    data = data.append(d3)

    # Select the data
    hits = gpd.GeoDataFrame(list(filter(prep_geom.contains, list(data['geometry'].values))), columns=['geometry'], crs=data.crs)
    result = gpd.sjoin(hits, data, op='contains')

    # Drop unnecessary index of the right df from join
    result = result.drop('index_right', axis=1)

#    ax = buffer.plot()
#    ax = dissolved.plot(ax=ax, color='white')
#    result.plot(ax=ax, color='gray')

    # Save to disk
    result.to_file(outfp)

