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

# reduce to GACC region - intersect w/ boundaries
gacc_path = '/projects/my-public-bucket/gaccRegions'
gacc_boundaries = gpd.read_file(gacc_path)
final_gacc_region = None

# @TODO: list all gacc name entires -> form dict between those and crawler words

if final_gacc_region is None:
    gacc_keyword = 'unsure'

# @TODO: extract year from large fire

# feds output path
feds_final_path = '/projects/shared-buckets/gsfc_landslides/FEDSoutput-s3-conus/WesternUS/2019/Largefire/*4655*' 


# CALL MAIN CRAWLER 

# instructions
# if name:
print('Enter your search keyword.')
print('NOTE: Enter incident name in ALL lower case with no "Fire" or "fire" term. Please avoid underscores. Include spaces in between for names i.e. Creek Forest, not CreekForest for optimal results')
# else: pass only year/region to return URLs / dirs
# stop at short depth(?) or provide all possible URLs?
print('To narrow your search, enter the GACC region(s) You would like to search.')
gacc_zones = ["alaska", "calif_n", "calif_s", "california_statewide", "eastern", "great_basin", "n_rockies", "pacific_nw", "rocky_mtn", "southern", "southwest"]
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