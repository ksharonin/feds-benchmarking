""" 
Input_VEDA Class

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

class InputVEDA():
    """ InputVEDA
        Object representing VEDA 
        E.g. firenrt dataset 
        https://nasa-impact.github.io/veda-docs/notebooks/tutorials/mapping-fires.html
    """
    
    # global
    TITLE_SETS = ["firenrt", "staging-stac", "staging-raster"]

    OGC_URLS = { "firenrt":  "https://firenrt.delta-backend.com",
                "staging-stac": "https://staging-stac.delta-backend.com",
                "staging-raster" : "https://staging-raster.delta-backend.com" }
    
    def __init__(self, title: str, 
                 collection: str, 
                 access_type="api": str,
                 usr_start: str,
                 usr_stop: str,
                 usr_bbox: list,
                 
                 ):
        
        # USER INPUT / FILTERS
        # TODO: FOR CERTAIN SEARCHES NEED DEFAULT TO SATISFY
        self._title = title
        self._collection = collection
        self._access_type = access_type
        self._usr_start = usr_start
        self._usr_stop = usr_stop
        self._usr_bbox = usr_bbox
        
        # PROGRAM SET
        self._api_url = None
        self._ds_bbox = None
        self._crs = None
        self._units = None
        self._range_start = None
        self._range_stop = None
        self._polygons = None
        
        # set up
        if access_type == "api":
            assert title in InputVEDA.TITLE_SETS, "ERR INPUTVEDA: Invalid title provided"
            self.set_api_url()
            self.fetch_api_collection()
        else:
            logging.warning('API NOT SELECTED: discretion advised due to direct file access.')
            self.set_hard_dataset()
    
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
        return self._range_start
    
    @property 
    def range_stop(self):
        return self._range_stop
    
    @property
    def polygons(self):
        return self._polygons
    
    
    # API DATA ACCESS
    @classmethod
    def set_api_url(self):
        """ fetch api url based on valid title"""
        if self._title in InputVEDA.OGC_URLS:
            self._api_url = OGC_URLS[title]
            
    
    @classmethod
    @ds_bbox.setter
    @crs.setter
    @range_start.setter
    @range_stop.setter
    def fetch_api_collection(self) -> dict:
        """ return collection using url + set up instance attributes"""
        
        assert self._api_url is not None, "ERR INPUTVEDA: cannot fetch with a null API url"
        
        # read out
        get_collections = Features(url=self._api_url).feature_collections()
        perm = get_collections.collection(self._collection)
        
        # set extent info with properties 
        self._ds_bbox = perm["extent"]["spatial"]["bbox"]
        self._crs = perm["extent"]["spatial"]["crs"]
        self._range_start = perm["extent"]["temporal"]["interval"][0][0]
        self._range_stop = perm["extent"]["temporal"]["interval"][0][1]
        
        return perm
    
    @classmethod
    @polygons.setter
    def set_polygons(self):
        """ fetch polygons from collection of interest; called with filter params from user
            fetch all filters from instance attributes
        """
        
        if self._title == "firenrt":
            perm_results = w.collection_items(
                self._collection,  # name of the dataset we want
                bbox=["-106.8", "24.5", "-72.9", "37.3"],  # coodrinates of bounding box,
                datetime=[last_week + "/" + most_recent_time],  # date range
                limit=1000,  # max number of items returned
                filter="farea>5 AND duration>2",  # additional filters based on queryable fields
            )
        else:
            # TODO
            logging.error(f"ERR INPUTVEDA: no setting method for this _title: {self._title}")
        
        self._polygons = perm_results
    
    
    # HARDCODED DATA ACCESS
    # TODO
    @classmethod
    @crs.setter
    @units.setter
    def set_hard_dataset(self):
        """ read data from passed url/location"""
        
        self._crs = CRS.from_user_input(int(crs))
        self._units = self.crs.axis_info[0].unit_name
        