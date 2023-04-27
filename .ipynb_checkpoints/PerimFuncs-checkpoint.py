""" PerimFuncs
This is the module containing all functions used in this project (excluding FTP)
"""
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

# @TODO: FINISH CHECK -add s3 path/validity check w boto3
# @TODO: implement error calculation according to yang's figs
# @TODO: implement TN calculation by bounding box method - trueNeg() method

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
def best_simplification(feds, nifc, top_performance, top_tolerance, base_tolerance, calc_method, lowerPref):
    """ feds: feds source
        nifc: external source to compare to
        top_performance: best numeric value (default is worst value aka > 100 % error)
        top_tolerance: corresponding simplification with best performance
        base_tolerance: counter for tracking progress from limit -> 0
        calc_method
        lowerPref: true if a "better" score is considered a lower value
        
        return: top_tolerance (best tolerance value from recursion)
    
    """
    if base_tolerance == 0:
        return top_tolerance
    
    # simplify + calculate performance
    simplified_feds = simplify_geometry(feds, base_tolerance)
    curr_performance = calc_method(simplified_feds, nifc)
     
    # if performance "better" (depends on passed bool / method) -> persist
    if curr_performance < top_performance and lowerPref:
        top_performance = curr_performance
        top_tolerance = base_tolerance
    elif curr_performance > top_performance and not lowerPref:
        top_performance = curr_performance
        top_tolerance = base_toleranc
    
    # reduce and keep recursing down
    base_tolerance -= 1
    
    return best_simplification(feds, nifc, top_performance, top_tolerance, base_tolerance, calc_method, lowerPref)

# terms:
# FEDS data are considered as the predicted class. 
# TN: True Negative; FN: False Negative; FP: False Positive; 
# TP: True Positive; FEDS_UB: Unburned area from FEDS; 
# FEDS_B: Area burned from FEDS; FRAP_UB: Unburned area from FRAP; 
# FRAP_B: Burned area from FRAP; AREA_TOTAL: Total land area in California.

def areaCalculation(geom_instance):
    """ Calculate area of the object, including
        mult-row instances via loop
        Input: geom data frame instance
        Output: numeric area calculation (units defined in const)
    """
    try:
        area = 0
        for i in range(geom_instance.geometry.area.shape[0]):
            area += geom_instance.geometry.area[i]
    except KeyError:
        # print('Identified key error in areaCalculation(): returning item() based area calc', end='\r')
        area = geom_instance.geometry.area.item()
    
    return area

def trueNeg(feds_inst, nifc_inst):
    """ Calculate true negative (agreeing on no geom)
        input: two geo dataframes
        output: area where both agree of no geom
    """
    return None

def ratioCalculation(feds_inst, nifc_inst):
    """ Calculate ratio defined in table 6:	
        FEDS_B/REF_B(urned area)
    """
    # sum area (since mul entries may exist) up by calc
    feds_area = areaCalculation(feds_inst)
    nifc_area = areaCalculation(nifc_inst)
    
    assert feds_area is not None, "None type detected for area; something went wrong"
    assert nifc_area is not None, "None type detected for area; something went wrong"
    
    return feds_area / nifc_area

def accuracyCalculation(feds_inst, nifc_inst):
    """ Calculate accuracy defined in table 6:
        (TP+TN)/AREA_TOTAL
        
        TN == agreed inverse by bounding box
        TP == FRAP + FEDS agree on burned (intersect)
    """
    # generate bounding box fitting both instances (even if multi-poly)
    
    # subtract feds_inst and nifc_inst from bounding area
    
    # TN = calculate intersection of both "negatives"
    
    return 0

# @TODO: call percision calculation func
def precisionCalculation(feds_inst, nifc_inst):
    """ TP/FEDS_B
        TP == FRAP + FEDS agree on burned (intersect)
        FEDS_B == all burned of feds 
    """
    assert isinstance(feds_inst, pd.DataFrame) and isinstance(nifc_inst, pd.DataFrame), "Object types will fail intersection calculation; check inputs"
    # calculate intersect (agreement) -> divide
    overlay = gpd.overlay(feds_inst, nifc_inst, how='intersection')
    TP = areaCalculation(overlay) # overlay.geometry.area.item()
    feds_area = areaCalculation(feds_inst)
    
    return TP / feds_area

def recallCalculation(feds_inst, nifc_inst):
    """ TP/REF_B (nifc)
        TP == FRAP + FEDS agree on burned (intersect)
        REF_B == all burned of nifc/source
    """
    TP = gpd.overlay(feds_inst, nifc_inst, how='intersection')
    nifc_area = areaCalculation(nifc_inst)
    
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
    symm_area = areaCalculation(sym_diff)
    nifc_area = areaCalculation(nifc_inst)
    # symmDiff_ratio = sym_diff.geometry.area.item() / nifc_inst.geometry.area.item()
    symmDiff_ratio = symm_area / nifc_area
    
    return symmDiff_ratio