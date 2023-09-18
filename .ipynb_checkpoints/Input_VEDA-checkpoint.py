""" 
Input_VEDA Class

"""

# import statements
from owslib.ogcapi.features import Features
import geopandas as gpd
import datetime as dt
from datetime import datetime, timedelta

class InputVEDA():
    """ InputVEDA
        Object representing VEDA 
        E.g. 
    """
    
    # global variables here
    FIRE_OGC_URL = "https://firenrt.delta-backend.com"
    
    # instance initiation
    def __init__(self, crs, title, access_type, ):
        self.crs = crs
        self.title = title
        self.access_type = access_type
         
          
    # attribute access
    def get_crs(self):
        return self.crs
    
    def read_API(self):
        """ API Read """
        return 0