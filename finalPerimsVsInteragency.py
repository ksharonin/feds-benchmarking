# activate env-feds env
import osgeo
import geopandas as gpd
import pandas as pd
from osgeo import ogr
import numpy as np
from matplotlib import pyplot as plt
import os
import xarray as xr
import rasterio
import glob
from shapely.errors import ShapelyDeprecationWarning
from shapely.geometry import Point
import shapely.speedups
import warnings
import folium
from folium import plugins
warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning) 
from datetime import datetime


# constants
perims_path = "/projects/my-public-bucket/InterAgencyFirePerimeterHistory"
williams_final_path = '/projects/shared-buckets/gsfc_landslides/FEDSoutput-s3-conus/WesternUS/2019/Largefire/*4655*'
usa_path = "/projects/my-public-bucket/USAShapeFile"
use_final = True
layer = 'perimeter'
ascending = False # NOTE: use var as indicator for plot ordering
date_column = 'DATE_CUR' # column corresponding to source date of perim (i.e. date for comparison against output) 

# change the global options that Geopandas inherits from
pd.set_option('display.max_columns',None)

# gpd method (comp. slower)
df = gpd.read_file(perims_path)
usa = gpd.read_file(usa_path)

# basic filtering
# remove none geometry 
non_empty = df[df.geometry != None]
# remove null acres
non_null = non_empty[non_empty.GIS_ACRES != 0]
finalized_perims = non_null
# NOTE: filtering by 'final' label established by NIFC is unreliable
# finalized_perims = non_empty[non_empty.FEATURE_CA == 'Wildfire Final Perimeter']

# Williams ID based path
lf_files = glob.glob(williams_final_path)
# unique lf ids if more than one, but works with only one too!
lf_ids = list(set([file.split('Largefire/')[1].split('_')[0] for file in lf_files])) 
print('Number of LF ids:',len(lf_ids)) # Should be one, just william's flats

# save set of fire(s) into single var depending on mode

# extract latest entry by ID
largefire_dict = dict.fromkeys(lf_ids)
for lf_id in lf_ids:
    most_recent_file = [file for file in lf_files if lf_id in file][-1]
    largefire_dict[lf_id] = most_recent_file
gdf = gpd.read_file(largefire_dict[lf_id],layer=layer)
# sort by descending time (latest to newest)
gdf = gdf.sort_values(by='t',ascending=ascending)

if use_final:
    print('BENCHMARKING: FINAL PERIM V. MODE')
    # read perimeter of existing line
    fid = lf_ids[0]
    max_timestamp = gdf.t.max()
    gdf = gdf[gdf.t == max_timestamp]
    # rename for convennience
    finalized_williams = gdf.iloc[[0]]
    assert finalized_williams.shape[0] == 1, "Somethings wrong, multiple perims detected..."
    # extract year for filtering
    extracted_year = max_timestamp.year
    
    
else:
    # @TODO: YEAR CHECK
    print('BENCHMARKING: EVOLVING FIRE PERIM V. MODE')
    mul_years = False
    finalized_williams = gdf 
    # check year uniformity
    sample_year = finalized_williams.iloc[[0]].t.max().year
    year_matching = [sample_year ==  finalized_williams.iloc[[j]].t.max().year for j in range(finalized_williams.shape[0])]
    # if there was any mismatch, flag for difference
    if False in year_matching:
        print('WARNING: Current LargeFire contains 2+ years; NIFC filtering impacted.')
        mul_years = True
        # start edge case
        # @TODO: update handling of edge case for filtering

# adjust CRS - assumes uniform crs
try:
    print('Attempting set_crs...')
    finalized_perims.set_crs(finalized_williams.crs)
except: 
    print('Failure: attempting to_crs application')
    print(finalized_williams.crs)
    finalized_perims = finalized_perims.to_crs(finalized_williams.crs)
    print(finalized_perims.crs)

assert finalized_williams.crs == year_perims.crs, "CRS mismatch"

# filter by year if year available
try:
    extracted_year
    year_perims = finalized_perims[finalized_perims.FIRE_YEAR == str(extracted_year)]
except NameError:
    print('WARNING: No year extracted from FEDS output. Setting to None. No year reduction applied.')
    extracted_year = None 
    year_perims = finalized_perims

# root out none types
year_perims['DATE_NOT_NONE'] = year_perims.apply(lambda row : row.DATE_CUR is not None, axis = 1)
year_perims = year_perims[year_perims.DATE_NOT_NONE == True]

# root out long-len date instances
# @TODO: origin of these dates? just wrong user control? way to salvage them reliably?
try:
    year_perims['DATE_LEN_VALID'] = limited.apply(lambda row : len(row.DATE_CUR) == 8 , axis = 1)
    year_perims = year_perims[year_perims.DATE_LEN_VALID == True]
except TypeError as e: 
    # if none detected, missed by filtering - check non existence
    print('Invalid type passed for lenght validation; check for Nones in set')
    

# @TODO: transform NIFC str columns to new datetime object col
year_perims['DATE_CUR_STAMP'] = 

# case 1: single NIFC match
# @TODO: find the closet date/time match - DATE_CUR col
# closest time --> intersect for performance
# vs. mul intersects --> closest time? --> issue is that it assumes closest will share

# one NIFC-perim pair only
# if NIFC not seen before -> form new pair
# if seen -> skip 

# @QUESTION: is right to assume intersecting is the best date match?

# nifc-perim pairs
comparison_pairs = []

# per FEDS output perim
for instance in range(finalized_williams.shape[0]):
    # extract time stamp
    timestamp = finalized_williams.iloc[[instance]].t
    # query matching nifc with year-month-day form
    
    
    # identify NIFC intersections
    resulting = gpd.overlay(year_perims,finalized_williams.iloc[[instance]], how='intersection')
    # 

    
# case 2: multiple NIFC matches:
 
# per pair run comparison
for nifc_perim_pair in comparison_pairs:
    

# storage? best for caching / re-running?

# access to alternative FEDS OUTPUT? 
