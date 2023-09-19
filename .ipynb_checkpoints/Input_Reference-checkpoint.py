""" 
Input_Reference Class

"""

import glob
import logging
import pandas as pd
import geopandas as gpd
from pyproj import CRS
from owslib.ogcapi.features import Features
import geopandas as gpd
import datetime as dt
from datetime import datetime, timedelta
from functools import singledispatch

class InputReference():
    """ InputReference
        Object representing an input polygon that is compared to a VEDA object
        E.g. 
    
    """
    
    # global variables here
    
    # instance initiation
    def __init__(self, title: str, 
                 usr_start: str,
                 usr_stop: str,
                 usr_bbox: list,
                 access_type="local": str,
                 custom_filter=False: str,
                ):
        
        # predefined sets (where methods exist)
        REFERENCE_PREDEFINED_SETS = ["nifc_local", "nifc_arcgis", "calfire_arcgis"]
        ACCESS_TYPE = ["local", "arcgis_online", "ftp_server", "aws_s3", "custom_api", "other"]
        # url maps
        NIFC_LOCAL = "/projects/my-public-bucket/InterAgencyFirePerimeterHistory"
        NIFC_ARCGIS = ""
        USA_SHP = "/projects/my-public-bucket/USAShapeFile"
        
        # USER INPUT / FILTERS
        self._title = title
        self._usr_start = usr_start
        self._usr_stop = usr_stop
        self._usr_bbox = usr_bbox
        self._access_type = access_type
        self._custom_filter = custom_filter
        
        # PROGRAM SET
        self._ds_bbox = None
        self._crs = None
        self._units = None
        self._ds_start = None
        self._ds_stop = None
        self._polygons = None
            
            
    @property
    def units(self):
        return self._units
    
    @property
    def ds_bbox(self):
        return self._ds_bbox
    
    @property
    def crs(self):
        return self._crs
    
    @property
    def range_start(self):
        return self._ds_start
    
    @property 
    def range_stop(self):
        return self._ds_stop
    
    @property
    def polygons(self):
        return self._polygons
    
    
    # NIFC
    def read_nifc_local(self):
        """ read local nifc file for polygons """
        # TODO
        return 0
    
    def read_nifc_arcgis(self):
        """ access arcgis services for nifc polygons """
        # TODO
        return 0
    
    
    # CALFIRE
    
    
    # OTHER - GENERIC
    
    