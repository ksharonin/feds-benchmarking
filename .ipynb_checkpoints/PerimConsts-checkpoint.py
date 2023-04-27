""" PerimConsts
This is the module containing all constants used in this project as well as the
running controls
"""

import glob
import pandas as pd
import geopandas as gpd
from pyproj import CRS

# ------------------------------------------------------------------------------
# project directories
# ------------------------------------------------------------------------------
perims_path = "/projects/my-public-bucket/InterAgencyFirePerimeterHistory"
williams_final_path = '/projects/shared-buckets/gsfc_landslides/FEDSoutput-s3-conus/WesternUS/2019/Largefire/*4655*'
usa_path = "/projects/my-public-bucket/USAShapeFile"

# ------------------------------------------------------------------------------
# geojson run control / path
# ------------------------------------------------------------------------------
# if want to use extent set
files = glob.glob("/projects/shared-buckets/ashiklom/WesternUS/files_for_paper/*_.geojson")
data_all = pd.concat([gpd.read_file(file) for file in files],ignore_index=True)
geojson_use = False
geojson_keyword = 'WILLIAMS FLATS' # 'KINCADE'

# ------------------------------------------------------------------------------
# CRS controls
# ------------------------------------------------------------------------------
default_crs = 9311 # 4326 # select CRS to apply e.g.'epsg:9311' -> 9311 as int
crs_object = CRS.from_user_input(default_crs)
fetch_unit = crs_object.axis_info[0].unit_name
# unit_dict = {'epsg:9311': 'metre', 'epsg:4326':'degree'}
unit_preference = fetch_unit # unit of choice @TODO double check plot impact

# ------------------------------------------------------------------------------
# main run controls
# ------------------------------------------------------------------------------
use_final = False # use last perimeter if True, use evolving perimeters if False (all perims on last largefire file)
layer = 'perimeter'
ascending = False # plot in descending + analysis in last to first
date_column = 'DATE_CUR' # column corresponding to source date of perim (i.e. date for comparison against output) - change according to source 
curr_dayrange = 5 # day range search; values [0,7] available, 1 recommended for 0 hour <-> 12 hour adjustments
apply_Wildfire_Final_Perimeter = False # apply the NIFC label based filtering - WARNING: unreliable given inconsistency
simplify_tolerance = 100 # user selected tolerance upper bound
apply_simplify = True # flip simplify performance
# for now place artificial barrier to prevent extreme draw of resources
# if apply_simplify:
    # assert use_final, "Artificial stop; apply_simplify and multiple perims enabled; check PerimConsts.py"
    
# ------------------------------------------------------------------------------
# FTP crawler consts
# ------------------------------------------------------------------------------
# gacc region path + file
gacc_path = '/projects/my-public-bucket/gaccRegions'
gacc_boundaries = gpd.read_file(gacc_path)
# region keys
gacc_keys = ['OSCC', 'SWCC', 'GBCC', 'RMCC', 'AICC', 'NWCC', 'NRCC', 'ONCC', 'EACC', 'SACC']
assert gacc_boundaries.GACCAbbrev.tolist() == gacc_keys, "Gacc keys order unexpected; check input file (see if sort is random)"
# associated regions with FTP server
# @NOTE: exclude "california_statewide" label (no fires (?) in that dir)
ftp_names = ["alaska", "calif_n", "calif_s", "eastern", "great_basin", "n_rockies", "pacific_nw", "rocky_mtn", "southern", "southwest"]
ftp_names_reordered = ["calif_s", "southwest", "great_basin", "rocky_mtn", "alaska", "pacific_nw", "n_rockies", "calif_n", "eastern", "southern"] 
assert ftp_names.sort() == ftp_names_reordered.sort(), "Extra check if any spell errors occured"
# finalized gacc <-> ftp server dict
assert len(gacc_keys) == len(ftp_names_reordered)
gacc_name_dict = dict(zip(gacc_keys, ftp_names_reordered))
# start site for all FTP searches
starting_URL = 'https://ftp.wildfire.gov/public/incident_specific_data/'