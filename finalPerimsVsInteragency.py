# activate env-feds env
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
from tqdm import tqdm
from matplotlib import pyplot as plt
from osgeo import ogr

# dev notes/todos:
# @TODO: rename "finalized_williams" var to elim confusion for generalized v.
# @TODO: call path validity checks/finish path check
# @TODO: create/add in CRS mapping dictionary
# @TODO: test run simplify + use PerimConsts.simplify_tolerance for control

# CONSTANTS
import PerimConsts

# FUNCTION DEFINITIONS

# @TODO: FINISH CHECK -add s3 path/validity check w boto3
def path_exists(path, ptype):
    """ Check if path exists (regular OS or s3)
            path == url to check
            ptype == "reg" vs "s3"
        return: boolean
    """
    
    if ptype == 's3':
        # @TODO: fix s3 check (unable to load in)
        s3 = boto3.resource('s3')

        try:
            s3.Object(directory, object_file).load()
            return True 
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                # The object does not exist.
                assert -1 == 0, "Failed s3 reading, object DNE"
                return False
            else:
                assert -1 == 0, "Failed s3 reading, non 404."
                return False
    else:
        # @TODO: run regular os check
        return False

def get_nearest(dataset, timestamp, dayrange):
    """ Identify rows of dataset with timestamp matches;
        expects year, month, date in datetime format
            dataset: input dataset to search for closest match
            timestamp: timestamp we want a close match for
        returns: dataset with d->m->y closest matches
    """
    assert dayrange < 8, "Excessive provided day range; select smaller search period."
    
    timestamp = timestamp.item()
    transformed = dataset.DATE_CUR_STAMP.tolist()

    clos_dict = {
      abs(timestamp.timestamp() - date.timestamp()) : date
      for date in transformed
    }

    res = clos_dict[min(clos_dict.keys())]
    # print("Nearest date: " + str(res))
    
    # check on dayrange flexibility
    if abs(timestamp.day - res.day) > dayrange and dayrange == 7:
        # trigger exception
        return None
    
    assert abs(timestamp.day - res.day) <= dayrange, "No dates found in specified range; try a more flexible range by adjusting `dayrange` var"
    
    # fetch rows with res timestamp
    finalized = dataset[dataset['DATE_CUR_STAMP'] == res]
    
    return finalized

# reduce/simplify geom
def simplify_geometry(shape, tolerance):
    """ shape: to simplify
        tolerance: passed to shapely tol
        return: simplified shape
    """
    # keep preserve_topology as default (true)
    assert isinstance(shape, gpd.GeoDataFrame)
    return shape.geometry.simplify(tolerance)

# @TODO: finish implementing recursive function on simplification calc
def best_simplification(feds, nifc, top_performance, top_tolerance, base_tolerance, calc_method):
    """ feds: feds source
        nifc: external source to compare to
        top_performance: best numeric value (default is worst value aka > 100 % error)
        top_tolerance: corresponding simplification with best performance
        base_tolerance: counter for tracking progress from limit -> 0
        calc_method
        
        return: top_tolerance (best tolerance value from recursion)
    
    """
    if base_tolerance == 0:
        return top_tolerance
    
    # calculate performance
    simplified_feds = simplify_geometry(feds, base_tolerance)
    
    # @TODO: make sure regardless of calc, order is proper
    curr_performance = calc_method(simplified_feds, nifc)
    # if performance better -> persist
    if curr_performance < top_performance:
        top_performance = curr_performance
        top_tolerance = base_tolerance
    
    # reduce and keep recursing down
    base_tolerance -= 1
    
    return best_simplification(feds, nifc, top_performance, top_tolerance, base_tolerance)

# @TODO: implement error calculation according to yang's figs

# terms:
# FEDS data are considered as the predicted class. 
# TN: True Negative; FN: False Negative; FP: False Positive; 
# TP: True Positive; FEDS_UB: Unburned area from FEDS; 
# FEDS_B: Area burned from FEDS; FRAP_UB: Unburned area from FRAP; 
# FRAP_B: Burned area from FRAP; AREA_TOTAL: Total land area in California.

def ratioCalculation(feds_inst, nifc_inst):
    """ Calculate ratio defined in table 6:	
        FEDS_B/REF_B(urned area)
    """
    feds_area = feds_inst.geometry.area.item()
    nifc_area = nifc_inst.geometry.area.item()
    
    assert feds_area is not None, "None type detected for area; something went wrong"
    assert nifc_area is not None, "None type detected for area; something went wrong"
    
    return feds_area / nifc_area

def accuracyCalculation():
    """ Calculate accuracy defined in table 6:
        (TP+TN)/AREA_TOTAL
        
        TN == ???
        TP == FRAP + FEDS agree on burned (intersect)
    """
    
    return 0

# @TODO: call percision calculation func
def precisionCalculation(feds_inst, nifc_inst):
    """ TP/FEDS_B
        TP == FRAP + FEDS agree on burned (intersect)
        FEDS_B == all burned of feds 
    """
    assert isinstance(feds_inst, pd.DataFrame) and isinstance(nifc_inst, pd.DataFrame), "Object types will fail intersection calculation; check inputs"
    # calculate intersect (agreement) -> divide
    TP = gpd.overlay(feds_inst, nifc_inst, how='intersection')
    feds_area = feds_inst.geometry.area.item()
    
    return TP / feds_area

def recallCalculation(feds_inst, nifc_inst):
    """ TP/REF_B (nifc)
        TP == FRAP + FEDS agree on burned (intersect)
        REF_B == all burned of nifc/source
    """
    TP = gpd.overlay(feds_inst, nifc_inst, how='intersection')
    nifc_area = nifc_inst.geometry.area.item()
    
    return TP / nifc_area

def IOUCalculation(feds_inst, nifc_inst):
    """ IOU (inter over union)
        TP/(TP + FP + FN)
    """
    TP = gpd.overlay(feds_inst, nifc_inst, how='intersection')
    FP = 0 # feds + nifc agree on no burning
    FN = 0 # feds thinks unburned when nifc burned
    
    return 0

def f1ScoreCalculation(feds_inst, nifc_inst):
    """ 2 * (Precision * Recall)/(Precision + Recall)
    """
    precision = precisionCalculation(feds_inst, nifc_inst)
    recall = recallCalculation(feds_inst, nifc_inst)
    calc = 2 * (precision*recall)/(precision+recall)
    
    return calc

# @TODO: custom calc functions
def symmDiffRatioCalculation(feds_inst, nifc_inst):
    """ symmetric difference calc, ratio 
        NOTE: error relative to NIFC/external soure
    """
    sym_diff = feds_inst.symmetric_difference(nifc_inst, align=False)
    # use item() to fetch int out of values
    assert sym_diff.shape[0] == 1, "Multiple sym_diff entries identified; pair accuracy evaluation will fail."
    # calculate error percent: (difference / "correct" shape aka nifc)
    symmDiff_ratio = sym_diff.geometry.area.item() / nifc_inst.geometry.area.item()
    
    return symmDiff_ratio


# MAIN CODE 

# change the global options that Geopandas inherits from
# gpd method (comp. slower)
pd.set_option('display.max_columns',None)

# read nifc perims + us
df = gpd.read_file(PerimConsts.perims_path)
# usa = gpd.read_file(PerimConsts.usa_path)

# basic filtering - remove none / null geometry 
non_empty = df[df.geometry != None]
non_null = non_empty[non_empty.GIS_ACRES != 0]
finalized_perims = non_null
# NOTE: filtering by 'final' label established by NIFC is UNRELIABLE!
if PerimConsts.apply_Wildfire_Final_Perimeter:
    print(f'WARNING: {PerimConsts.apply_Wildfire_Final_Perimeter} is true; may severely limit search results.')
    assert 'FEATURE_CA' in non_emptys.columns, ""
    finalized_perims = non_empty[non_empty.FEATURE_CA == 'Wildfire Final Perimeter']

if PerimConsts.geojson_use:
    # check selected key in list
    data_all = PerimConsts.data_all
    all_names = data_all['Name'].tolist()
    assert PerimConsts.geojson_keyword in all_names, "Selected geojson_keyword not in GeoJson, check constants."
    # read geojson
    gdf = data_all[data_all['Name']==geojson_keyword].copy()
    gdf = gdf.sort_values(by='t',ascending=PerimConsts.ascending)
else: 
    # Williams ID based path
    lf_files = glob.glob(PerimConsts.williams_final_path)
    # unique lf ids if more than one, but works with only one too!
    lf_ids = list(set([file.split('Largefire/')[1].split('_')[0] for file in lf_files])) 
    print('Number of LF ids:',len(lf_ids)) # Should be one, just william's flats

    # save set of fire(s) into single var depending on mode

    # temporary check
    assert len(lf_ids) != 0, "lf_ids is empty, halt algorithm."

    # extract latest entry by ID
    largefire_dict = dict.fromkeys(lf_ids)

    for lf_id in lf_ids:
        most_recent_file = [file for file in lf_files if lf_id in file][-1]
        largefire_dict[lf_id] = most_recent_file

    gdf = gpd.read_file(largefire_dict[lf_id],layer=PerimConsts.layer)
    # sort by descending time (latest to newest)
    gdf = gdf.sort_values(by='t',ascending=PerimConsts.ascending)

if PerimConsts.use_final:
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
    
    # if there was any mismatch, flag for difference (mul years)
    if False in year_matching:
        print('WARNING: Current LargeFire contains 2+ years; NIFC filtering impacted.')
        mul_years = True
        # start edge case
        # @TODO: update handling of edge case for filtering
        # print(f'all picked up timestamps: {finalized_williams.t.tolist()}')
        # iterate print years for mismatch
        for l in range(finalized_williams.shape[0]):
            year_fetch = finalized_williams.iloc[[l]].t.item().year
            if year_fetch != sample_year:
                print(f'failed year: sample was {sample_year} while {year_fetch} was detected.')
            
        assert not mul_years, "@TODO: catch edge case for years; force halt for now."
    
    # else: single year
    assert isinstance(sample_year, int), "sample year fails type match"
    extracted_year = sample_year
     
# adjust nifc CRS
try:
    print('Attempting set_crs (nifc)...')
    finalized_perims.set_crs(PerimConsts.default_crs)
except: 
    print('Failure: attempting to_crs application')
    finalized_perims = finalized_perims.to_crs(PerimConsts.default_crs)
    print(finalized_perims.crs)

# adjust FEDS crs 
try:
    print('Attempting set_crs (FEDS)...')
    finalized_williams.set_crs(PerimConsts.default_crs)
except: 
    print('Failure: attempting to_crs application')
    finalized_williams = finalized_williams.to_crs(PerimConsts.default_crs)
    print(finalized_williams.crs)

assert finalized_williams.crs == finalized_perims.crs, "CRS mismatch"
assert finalized_williams.crs.axis_info[0].unit_name == PerimConsts.unit_preference, f"finalized_williams fails unit check for: {PerimConsts.unit_preference}, current units: {finalized_williams.crs.axis_info[0].unit_name}"
assert finalized_perims.crs.axis_info[0].unit_name == PerimConsts.unit_preference, f"finalized_perims fails unit check for: {PerimConsts.unit_preference}"

# filter by year if year available
try:
    extracted_year
    year_perims = finalized_perims[finalized_perims.FIRE_YEAR == str(extracted_year)]
    
except NameError:
    print('WARNING: No year extracted from FEDS output. Setting to None. No year reduction applied.')
    extracted_year = None 
    year_perims = finalized_perims
    assert 1==0, "force stop -> make algorithm rely on year? otherwise doesnt seem efficient"

# root out none types
year_perims['DATE_NOT_NONE'] = year_perims.apply(lambda row : getattr(row, PerimConsts.date_column) is not None, axis = 1)
year_perims = year_perims[year_perims.DATE_NOT_NONE == True]

# root out long-len date instances
# @TODO: origin of these dates? just wrong user control? way to salvage them reliably?
try:
    year_perims['DATE_LEN_VALID'] = year_perims.apply(lambda row : len(getattr(row, PerimConsts.date_column)) == 8 , axis = 1)
    year_perims = year_perims[year_perims.DATE_LEN_VALID == True]
except TypeError as e: 
    # if none detected, missed by filtering - check non existence
    print('Invalid type passed for lenght validation; check for Nones in set')

# transform NIFC str to new datetime object
cur_format = '%Y%m%d' 
year_perims['DATE_CUR_STAMP'] =  year_perims.apply(lambda row : datetime.strptime(getattr(row, PerimConsts.date_column), cur_format), axis = 1)

# nifc-perim pairs as tuples
# i.e. (perimeter FEDS instance, NIFC match)
comparison_pairs = []

# per FEDS output perim -> get best NIFC match(es) by date
print('Per FEDS output, identify best NIFC match...')
for instance in tqdm(range(finalized_williams.shape[0])):
    # @TODO: run intersection first with all year_perims
    # @TODO: store all non-zero intersections -> get nearest time stamp set (?)
    # dont want to eliminate all matches that are one day apart
    
    # collection of indices relative to year_perims
    insc_indices = []
    # master matches with intersections/timestemp filtering
    intersd = []
    
    # iterate on all year_perims and inersect
    for insc in range(year_perims.shape[0]):
        # fetch nifc instance
        curr_nifc = year_perims.iloc[[insc]]
        intersect = gpd.overlay(curr_nifc,finalized_williams.iloc[[instance]], how='intersection')
        # cont if empty
        if not intersect.empty:
            insc_indices.append(insc)
        # else: continue
    
    if len(insc_indices) == 0:
        print('WARNING: insc_indices was none -> skipping step')
        continue
    
    # all current indices present get_nearest check opportunities
    # @TODO: change the get_nearest to apply for month...?
    timestamp = finalized_williams.iloc[[instance]].t
    # apply insc_indices to pick out intersect matches
    reduced = year_perims.take(insc_indices)
    # match run with get nearest
    # although its really picky -> try for now
    
    # print(f'VERBOSE: reduced: {reduced}, timestamp: {timestamp}')
    try:
        matches = get_nearest(reduced, timestamp, PerimConsts.curr_dayrange)
    except:
        # print('WARNING get_nearest failed: continue in instance comparison')
        # indicates no match in given range -> append to failure list 
        print(f'WARNING: Perim master row ID: {finalized_williams.iloc[[instance]].index} at index {instance} as NO INTERSECTIONS at closest date. Storing and will report 0 accuracy.')
        comparison_pairs.append((finalized_williams.iloc[[instance]], None))
        continue
        
    # all matches should act as intersd -> extract from DF
    if matches is None:
        # @TODO: improve handling -> likely just continue and report failed benching
        raise Exception('FAILED: No matching dates found even with 7 day window, critical benchmarking failure.')
        
    intersd = [matches.iloc[[ing]] for ing in range(matches.shape[0])]
    
    if matches is None:
        # @TODO: improve handling -> likely just continue and report failed benching
        raise Exception('FAILED: No matching dates found even with 7 day window, critical benchmarking failure.')

    
    if len(intersd) == 0:
        # print(f'WARNING: Perim master row ID: {finalized_williams.iloc[[instance]].index} at index {instance} as NO INTERSECTIONS at closest date. Storing and will report 0 accuracy.')
        # comparison_pairs.append((finalized_williams.iloc[[instance]], None))
        assert 1==0, "case shouldn't exist, throw exception"
        
    elif len(intersd) > 1:
        # if multiple have overlay -> store them with a warning 
        print(f'NOTICE: More thane 1, in total: {len(matches)} NIFC date matches, intersect with perimeter master row ID: {finalized_williams.iloc[[instance]].index} with index in finalized_willaims: {instance}, storing all as pairs')
        
        # iterate and generate tuple pairs; append to list
        [comparison_pairs.append((finalized_williams.iloc[[instance]], to_ap)) for to_ap in intersd]
            
    else:
        # single match -> append (perim instance, NIFC single match)
        comparison_pairs.append((finalized_williams.iloc[[instance]], intersd[0]))

# @NOTE: consider reworking store situation - iterating over list can be time consuming for feds perims
symmDiffNIFC_performance = []
# @TODO: define extray arrays for other calculations


# @TODO: store corresponding performance per single difference
makeup_feds = []
makeup_nifc = [] 
  

# @TODO ACCURACY CALCULATION: per pair run comparison
# calculate symmetrical difference
for nifc_perim_pair in comparison_pairs:
    
    # 0: feds instance, 1: nifc matces
    feds_inst = nifc_perim_pair[0]
    nifc_inst = nifc_perim_pair[1]
    
    # if none type, append 0 accuracy and cont
    if nifc_inst is None:
        symmDiffNIFC_performance.append(100)
        # @TODO: cover all other cases
        
        continue
    
    symm_ratio = symmDiffRatioCalculation(feds_inst, nifc_inst)
    # align calculations by index -> zip n store at end
    symmDiffNIFC_performance.append(symm_ratio)



# @NOTE: end for now just to see outputs
print('-----------------')
print('ANALYSIS COMPLETE')
print('-----------------')

assert len(symmDiffNIFC_performance) == len(comparison_pairs), "Mismatching dims for error performance v. comparison pairs, check resulting arrays"

print('Resulting error percentages for FEDS perimeter accuracy vs. closest intersecting NIFC:')
count_100 = 0
count_100_dates = []
for index in range(len(symmDiffNIFC_performance)):
    # fetch inst + components by index
    sam = symmDiffNIFC_performance[index]
    match_tuple = comparison_pairs[index]
    perim_output = match_tuple[0]
    nifc_perim = match_tuple[1]
    
    if sam == 100:
        # count and append date
        count_100 += 1
        count_100_dates.append(perim_output.t.item())
    else:
        print(f'For FEDS output perimeter at {perim_output.t.item()} and NIFC perimeter at {nifc_perim.DATE_CUR_STAMP.item()}, symmDiff ratio percent error of:')
        print(f'{sam*100}%')
print(f'{count_100} instances of 100% error')
print('FEDS output perimeter dates with no matches by threshold:')
print(count_100_dates)

# @TODO: implement proper units -> currently list w/ switch cases
    
# @TODO: ideal storage ideas? 
# idea: generate ipynb for visualization? 
# need to replace/write over if duplicates exist

# access to alternative FEDS OUTPUT? 
