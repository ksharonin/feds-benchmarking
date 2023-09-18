""" 
Input_VEDA Class

"""

# import statements

import glob
import logging
import pandas as pd
import geopandas as gpd
from pyproj import CRS
from owslib.ogcapi.features import Features
import geopandas as gpd
import datetime as dt
from datetime import datetime, timedelta

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
    
    # instance initiation
    def __init__(self, title: str, 
                 collection: str, 
                 access_type="api": str, 
                 ):
  
        # extract from crs
        self.units = self.crs.axis_info[0].unit_name
        # name for set - user input from choice
        self.title = title
        # collection name
        self.collection = collection
        # platform type
        self.access_type = access_type
        
        self.api_url = None
        self.bbox = None
        self.crs = None
        self.start = None
        self.stop = None
        
        
        if access_type == "api":
            assert title in InputVEDA.TITLE_SETS, "ERR INPUTVEDA: Invalid title provided"
            self.set_api_url()
            self.fetch_api_collection()
        else:
            logging.warning('API NOT SELECTED: discretion advised due to direct file access.')
    
    # API DATA ACCESS
    @classmethod
    def set_api_url(self):
        """ fetch api url based on valid title"""
        if self.title in InputVEDA.OGC_URLS:
            self.api_url = OGC_URLS[title]
            
    @classmethod           
    def fetch_api_collection(self) -> dict:
        """ return collection using url + set up instance attributes"""
        
        assert self.api_url is not None, "ERR INPUTVEDA: cannot fetch with a null API url"
        
        # read out
        get_collections = Features(url=self.api_url).feature_collections()
        perm = get_collections.collection(self.collection)
        
        # set extent info with properties 
        self.bbox = perm["extent"]["spatial"]["bbox"]
        self.crs = perm["extent"]["spatial"]["crs"]
        self.start = perm["extent"]["temporal"]["interval"][0][0]
        self.stop = perm["extent"]["temporal"]["interval"][0][1]
        
        return perm
    
    # HARDCODED DATA ACCESS
    @classmethod
    def read_hard_dataset(self):
        """ read data from passed url/location"""
        self.crs = CRS.from_user_input(int(crs))
        