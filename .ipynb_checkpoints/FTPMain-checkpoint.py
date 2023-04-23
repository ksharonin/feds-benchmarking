# FEDS evolving perims vs. NIFC FTP server - prototype
# assumptions:
# no name for FEDS: only timestamp/geometry

import osgeo
import geopandas as gpd
import pandas as pd
import numpy as np
import os
import xarray as xr
import rasterio
import glob
import shapely.speedups
import warnings
import folium
import boto3
import botocore

from shapely.errors import ShapelyDeprecationWarning
from shapely.geometry import Point
from folium import plugins
warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning) 
from datetime import datetime
from tqdm import tqdm # add in progress watch
from matplotlib import pyplot as plt
from osgeo import ogr

# global constants
geojson_use = True
geojson_keyword = 'BOULDER' # 'WILLIAMS FLATS' 
feds_final_path = '/projects/shared-buckets/gsfc_landslides/FEDSoutput-s3-conus/WesternUS/2019/Largefire/*4655*' #feds path
ascending = True

# read FEDS perims (geojson or regular)
pd.set_option('display.max_columns',None)

if geojson_use:
    # check selected key in list
    all_names = data_all['Name'].tolist()
    assert geojson_keyword in all_names, "Selected geojson_keyword not in GeoJson, check constants."
    # read geojson
    gdf = data_all[data_all['Name']==geojson_keyword].copy()
    gdf = gdf.sort_values(by='t',ascending=ascending)
else: 
    # fire id based path
    lf_files = glob.glob(feds_final_path)
    # unique lf ids if more than one, but works with only one too!
    lf_ids = list(set([file.split('Largefire/')[1].split('_')[0] for file in lf_files])) 
    print('Number of LF ids:',len(lf_ids)) # Should be one

    assert len(lf_ids) != 0, "lf_ids is empty, halt algorithm."

    # extract latest entry by ID
    largefire_dict = dict.fromkeys(lf_ids)

    for lf_id in lf_ids:
        most_recent_file = [file for file in lf_files if lf_id in file][-1]
        largefire_dict[lf_id] = most_recent_file

    gdf = gpd.read_file(largefire_dict[lf_id],layer=layer)
    # sort by descending time (latest to newest)
    gdf = gdf.sort_values(by='t',ascending=ascending)

# crs catch/corrections
# @TODO: expand later to fix crs mismatches
assert gacc_boundaries.crs == gdf.crs, "mismatch crs"
    
# reduce to GACC region - intersect w/ boundaries
gacc_path = '/projects/my-public-bucket/gaccRegions'
gacc_boundaries = gpd.read_file(gacc_path)
gacc_keys = ['OSCC', 'SWCC', 'GBCC', 'RMCC', 'AICC', 'NWCC', 'NRCC', 'ONCC', 'EACC', 'SACC']
assert gacc_boundaries.GACCAbbrev.tolist() == gacc_keys, "Gacc keys order unexpected; check input file (see if sort is random)"
# @NOTE: exclude "california_statewide" label (no fires (?) in that dir)
ftp_names = ["alaska", "calif_n", "calif_s", "eastern", "great_basin", "n_rockies", "pacific_nw", "rocky_mtn", "southern", "southwest"]
ftp_names_reordered = ["calif_s", "southwest", "great_basin", "rocky_mtn", "alaska", "pacific_nw", "n_rockies", "calif_n", "eastern", "southern"] 
assert ftp_names.sort() == ftp_names_reordered.sort(), "Extra check if any spell errors occured"

# map gaccIDs from geo <-> ftp search words
gacc_name_dict = dict(gacc_boundaries, ftp_names_reordered)

# intersect fire to find GACC region
final_gacc_region = None 
intersection_main = gpd.overlay(gacc_boundaries, gdf, how='intersection')
assert not intersection_main.empty, "Empty dataframe, no intersection; visually inspect - if fire is global, it may be out of bounds for FTP match program"
all_abbrevs = intersection_main.GACCAbbrev.tolist()
num_unique = len(np.unique(all_abbrevs))
assert num_unique == 1, "More than one abbrev recieved -> NIFC edgecase detected. Manual search required."

if final_gacc_region is None:
    gacc_keyword = 'unsure'
    assert 1 == 0, "Forced stop; no GACC decided, manual search required since fire is potentially global/non-us"

# @TODO: extract year from large fire


# CALL MAIN CRAWLER 

# instructions
# if name:
print('Enter your search keyword.')
print('NOTE: Enter incident name in ALL lower case with no "Fire" or "fire" term. Please avoid underscores. Include spaces in between for names i.e. Creek Forest, not CreekForest for optimal results')
# else: pass only year/region to return URLs / dirs
# stop at short depth(?) or provide all possible URLs?
print('To narrow your search, enter the GACC region(s) You would like to search.')
print('IF YOU DO NOT KNOW THE REGION: please enter "unsure"')
print('Year')
print('Enter year from timestamp AS STRING. any error / misid should return as failure, no non-year search permitted')
# DEPTH INPUT
# This is optional - allows user to adjust the depth of search
# THIS CAN HIGHLY AFFECT RESULTS. DO NOT MODIFY UNLESS CONFIDENT.

print('OPTIONAL: if you would like to modify the extent of your search, please enter a depth (integer).')
print(' ')
print('!!! WARNING !!!')
print(' ')
print('The depth will HEAVILY impact your search! If you are just starting, do not modify the depth.')
print('Modify the depth ONLY if you are sure your files are at a deeper level.')
print('Higher depth == bigger search == slower results. If you modify with no motivation, your search will be slowed by a large factor.')

print(' ')
print('If you choose to change your depth, select values 9, 10, or 11')
print('Too high of a value may cause your search to fail!')