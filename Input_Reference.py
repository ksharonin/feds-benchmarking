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
    
    REFERENCE_PREDEFINED_SETS = ["nifc_local", "nifc_arcgis", "calfire_arcgis", "custom_shp", "custom_s3"]
    ACCESS_TYPE = ["defined", "custom"]
    NIFC_LOCAL = "/projects/my-public-bucket/InterAgencyFirePerimeterHistory"
    NIFC_ARCGIS = ""
    USA_SHP = "/projects/my-public-bucket/USAShapeFile"
    
    # instance initiation
    def __init__(self, title: str, 
                 usr_start: str,
                 usr_stop: str,
                 usr_bbox: list,
                 access_type="defined",
                 custom_filter=False,
                ):
        
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
    
    # GENERIC ACCESS 
    def read_shp_from_local(self):
        """ given a generic path in maap with access -> read polygon """
        # TODO
        return 0
    
    def read_arcgis_online(self):
        """ given a generic arcgis access -> accesspolygon """
        # TODO
        return 0
    
    # NIFC DATA PROCESSING
    def nifc_local_filters(self):
        return 0
    
    def nifc_arcgis_filters(self):
        return 0
    
    
    # CALFIRE DATA PROCESSING
    def calfire_local_filters(self):
        return 0
    
    def calfire_arcgis_filters(self):
        return 0
    