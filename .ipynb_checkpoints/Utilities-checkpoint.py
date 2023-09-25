""" Utilities.py

    for additional processing functions to connect class instances
"""

import glob
import logging
import sys
import pandas as pd
import geopandas as gpd
from pyproj import CRS
from owslib.ogcapi.features import Features
import geopandas as gpd
import datetime as dt
from datetime import datetime, timedelta


# USER INPUT PROCESSING
def format_datetime(year, month, day, hour, minute, second, tz_offset_hours, tz_offset_minutes, utc_offset) -> str:
    """ given integer vals, produce iso string formatted for VEDA processing """
    
    dt = datetime(year, month, day, hour, minute, second)
    tz_offset = timedelta(hours=tz_offset_hours, minutes=tz_offset_minutes)
    
    if tz_offset_hours < 0:
        dt -= abs(tz_offset)
    else:
        dt += tz_offset
    
    # ISO 8601 string + fix time zone addition for API search
    formatted_datetime = dt.isoformat()
    formatted_datetime = formatted_datetime + '+' + utc_offset
    
    return formatted_datetime

def check_bbox(bbox: list) -> bool:
    """ given bbox as list, check if all components valid """
    
    if not isinstance(bbox, list) or len(bbox) != 4:
        return False

    if not all(isinstance(element, str) for element in bbox):
        return False

    try:
        min_lon, min_lat, max_lon, max_lat = map(float, bbox)
        if -180.0 <= min_lon <= 180.0 and -90.0 <= min_lat <= 90.0 and -180.0 <= max_lon <= 180.0 and -90.0 <= max_lat <= 90.0:
            return True
    except ValueError:
        pass

    return False

def check_crs(crs_in: int) -> bool:
    """ given crs epsg as int, return crs object"""
    try:
        crs_object = CRS.from_user_input(crs_in)
        return True
    except Exception as gen_err:
        return False

# S3 PROCESSING & ACCESS
def split_s3_path(s3_path: str):
    """ for bucket and key extraction"""
    
    path_parts=s3_path.replace("s3://","").split("/")
    nested = False
    
    if len(path_parts) == 2:
        # only bucket + key
        bucket=path_parts.pop(0)
        key="/".join(path_parts)
        
    else:
        key = path_parts.pop()
        bucket = [path_parts[0], ""]
        for concat in path_parts[1:]:
            bucket[1] = bucket[1] + concat + "/"
        nested = True
    
    return bucket, key, nested

# DECORATORS
# TODO