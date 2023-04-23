""" PerimConsts
This is the module containing all constants used in this project as well as the
running controls
"""

import glob
import pandas as pd
import geopandas as gpd

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
default_crs = 'epsg:4326' # select CRS to apply e.g.'epsg:9311'
unit_dict = {'epsg:9311': 'metre', 'epsg:4326':'degree'}
unit_preference = unit_dict[default_crs] # unit of choice @TODO double check plot impact

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