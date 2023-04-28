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
# @TODO: jupyternb generation for visualization?
# @TODO: change the get_nearest to apply for month...? currently very strict

# CONSTANTS
import PerimConsts

# FUNCTION DEFINITIONS
import PerimFuncs

pd.set_option('display.max_columns',None)

# read nifc perims
df = gpd.read_file(PerimConsts.perims_path)
# us (for plotting/comparison)
# usa = gpd.read_file(PerimConsts.usa_path)

# basic filtering - remove none / null geometry 
# NOTE: filtering by 'final' label established by NIFC is UNRELIABLE!
non_empty = df[df.geometry != None]
non_null = non_empty[non_empty.GIS_ACRES != 0]
finalized_perims = non_null
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
    timestamp = finalized_williams.iloc[[instance]].t
    # apply insc_indices to pick out intersect matches
    reduced = year_perims.take(insc_indices)
    # match run with get nearest
    # although its really picky -> try for now
    
    # print(f'VERBOSE: reduced: {reduced}, timestamp: {timestamp}')
    try:
        matches = PerimFuncs.get_nearest(reduced, timestamp, PerimConsts.curr_dayrange)
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

# yang calc storage
ratios = []
accuracies = []
precisions = []
recalls = []
ious = []
f1s = []
# indepdent calc storage
symmDiffNIFC_performance = []
  

# calculate yang methods + additional indep methods
for nifc_perim_pair in comparison_pairs:
    
    # 0: feds instance, 1: nifc matces
    feds_inst = nifc_perim_pair[0]
    nifc_inst = nifc_perim_pair[1]
    
    # if none type, append 0 accuracy and cont
    if nifc_inst is None:
        ratios.append(None)
        accuracies.append(None)
        precisions.append(None)
        recalls.append(None)
        ious.append(None)
        f1s.append(None)
        symmDiffNIFC_performance.append(None)
        # @TODO: cover all other cases
        continue
    
    # yang calculations
    ratio = PerimFuncs.ratioCalculation(feds_inst, nifc_inst)
    accuracy = PerimFuncs.accuracyCalculation(feds_inst, nifc_inst)
    precision = PerimFuncs.precisionCalculation(feds_inst, nifc_inst)
    recall = PerimFuncs.recallCalculation(feds_inst, nifc_inst)
    iou= PerimFuncs.IOUCalculation(feds_inst, nifc_inst)
    f1 = PerimFuncs.f1ScoreCalculation(feds_inst, nifc_inst)
    # indep calc 
    symm_ratio = PerimFuncs.symmDiffRatioCalculation(feds_inst, nifc_inst)
    
    # SIMPLIFY TEST - symmDiff
    if PerimConsts.apply_simplify: 
        print('VERBOSE: entering recursive simplify proc')
        best_tol = PerimFuncs.best_simplification(feds_inst, nifc_inst, 1000000, 0, PerimConsts.simplify_tolerance, PerimFuncs.symmDiffRatioCalculation, True)
        print('TEST: best_tol from best_simplificatio()')
        print(best_tol)
    
    # align calculations by index -> zip n store at end
    symmDiffNIFC_performance.append(symm_ratio)
    ratios.append(ratio)
    accuracies.append(accuracy)
    precisions.append(precision)
    recalls.append(recall)
    ious.append(iou)
    f1s.append(f1)


# @NOTE: end for now just to see outputs
print('-----------------')
print('ANALYSIS COMPLETE')
print('-----------------')

# check sizing for all calculations
iteratei = [ratios, accuracies, precisions, recalls, ious, f1s]
for listy in iteratei:
    assert len(listy) == len(comparison_pairs), "Mismatching dims for error performance v. comparison pairs, check resulting arrays"
    
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
    
    # all items sharing index should correspond to a none result
    if sam is None:
        # count and append date
        count_100 += 1
        count_100_dates.append(perim_output.t.item())
    else:
        print(f'For FEDS output perimeter at {perim_output.t.item()} and NIFC perimeter at {nifc_perim.DATE_CUR_STAMP.item()}:')
        print(f'Ratio: {ratios[index]}')
        print(f'Accuracy: {accuracies[index]}')
        print(f'Precision: {precisions[index]}')
        print(f'Recall: {recalls[index]}')
        print(f'IOU: {ious[index]}')
        print(f'F1 Score: {f1s[index]}')
        print(f'symmDiff ratio percent error of: {sam*100}%')
        print(f'NOTE: all calculations in unit: {PerimConsts.unit_preference}')

print(f'{count_100} instances of 100% error / no calculations')
print('FEDS output perimeter dates with no matches by threshold:')
print(count_100_dates)

# @TODO: implement proper units -> currently list w/ switch cases
    
# @TODO: ideal storage ideas? 
# idea: generate ipynb for visualization? 
# need to replace/write over if duplicates exist

# access to alternative FEDS OUTPUT? 
