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
                 usr_start: str,
                 usr_stop: str,
                 usr_bbox: list,
                 access_type="api",
                 limit=1000,
                 custom_filter=False,
                 ):
        
        # USER INPUT / FILTERS
        self._title = title
        self._collection = collection
        self._access_type = access_type
        self._usr_start = usr_start
        self._usr_stop = usr_stop
        self._usr_bbox = usr_bbox
        self._srch_limit = limit
        self._custom_filter = custom_filter
        
        # PROGRAM SET
        self._api_url = None
        self._ds_bbox = None
        self._crs = None
        self._units = None
        self._range_start = None
        self._range_stop = None
        self._polygons = None
        self._queryables = None
        
        # set up
        if access_type == "api":
            assert title in InputVEDA.TITLE_SETS, "ERR INPUTVEDA: Invalid title provided"
            self.__set_api_url()
            self.__fetch_api_collection()
            self.__set_api_polygons()
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
    
    @property
    def queryables(self):
        return self._queryables
    
    
    # API DATA ACCESS
    def __set_api_url(self):
        """ fetch api url based on valid title"""
        if self._title in InputVEDA.OGC_URLS:
            self._api_url = InputVEDA.OGC_URLS[self._title]
            
        return self
            
    @ds_bbox.setter
    @crs.setter
    @range_start.setter
    @range_stop.setter
    @queryables.setter
    def __fetch_api_collection(self) -> dict:
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
        self._queryables = get_collections.collection_queryables(self._collection)["properties"]
        
        # return perm
        return self
    
    @polygons.setter
    def __set_api_polygons(self):
        """ fetch polygons from collection of interest; called with filter params from user
            fetch all filters from instance attributes
        """
        
        if self._title == "firenrt":
            
            # usr filter applied - assumes valid filter is passed
            if self._custom_filter:
                perm_results = Features(url=self._api_url).feature_collections().collection_items(
                    self._collection,  # name of the dataset we want
                    bbox= self._usr_bbox,  # coords of bounding box,
                    datetime=[self._usr_start + "/" + self._usr_stop],  # user date range
                    limit=self._srch_limit,  # max number of items returned
                    filter= ext_query,  # additional filters based on queryable fields
                )
            
            # no usr filter
            else:
                perm_results = Features(url=self._api_url).feature_collections().collection_items(
                    self._collection,  # name of the dataset we want
                    bbox= self._usr_bbox,  # coords of bounding box,
                    datetime=[self._usr_start + "/" + self._usr_stop],  # user date range
                    limit=self._srch_limit,  # max number of items returned
                )
                
        else:
            logging.error(f"ERR INPUTVEDA: no setting method for the _title: {self._title}")
            # TODO
        
        if not perm_results["numberMatched"] == perm_results["numberReturned"]:
            logging.warning('INPUTVEDA: provided limit cuts out items of possible interest; consider upping limit') 
            
        self._polygons = perm_results
        
        return self
        
    
    def load_api_polygons(self) -> gpd.geodataframe.GeoDataFrame:
        """ assuming __set_api_polygons successfully ran; load api polygons
             return associated geoDataFrame; can apply plotting, analysis to frame etc.
        """
        
        return gpd.GeoDataFrame.from_features(self._polygons["features"])
    
    
    
    # HARDCODED DATA ACCESS
    # TODO
    @crs.setter
    @units.setter
    def set_hard_dataset(self):
        """ read data from passed url/location"""
        
        self._crs = CRS.from_user_input(int(crs))
        self._units = self.crs.axis_info[0].unit_name
        