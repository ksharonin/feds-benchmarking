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
                 crs: str, ):
        
        # coordinate ref system
        self.crs = CRS.from_user_input(int(crs))
        # extract from crs
        self.units = self.crs.axis_info[0].unit_name
        # name for set - user input from choice
        self.title = title
        # set null till time 
        self.api_url = None
        # platform type
        self.access_type = access_type
        
        if access_type == "api":
            assert title in InputVEDA.TITLE_SETS, "ERR INPUTVEDA: Invalid title provided"
            self.set_api_url()
            self.set_api_collection()
        else:
            logging.warning('API NOT SELECTED: discretion advised due to direct file access.')
                                            
        
    def get_crs(self):
        return self.crs
                                            
    def set_api_url(self):
        """ fetch api url based on valid title"""
        if self.title in InputVEDA.OGC_URLS:
            self.api_url = OGC_URLS[title]
    
    def set_api_collection(self):
        """ set collection with title"""
        assert self.title is not None, "ERR INPUTVEDA: cannot fetch using null based title"
        
                
    def fetch_collection(self, collec_name: str):
        