""" 
Output_Calculation Class

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

class OutputCalculation():
    
    """ OutputCalculation
        Class representing 
    """
    
    def __init__(self, veda_input, ref_input):
        
        # reference originial polygons
        self.veda_input = veda_input
        self.ref_input = ref_input
        
        
    @classmethod
    def dump_to_file(self):
        # TODO
        return 0
    
    @classmethod
    def plot_results(self):
        # TODO
        return 0