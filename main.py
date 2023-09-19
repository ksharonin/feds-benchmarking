""" main.py
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

# while 1 

# USER INPUT
# for VEDA:
# -> time range(start/stop)
# -> bbox
# -> name
# -> collection of the title
# -> any extra filter matching queryable fields

# GENERATE
# VEDA input instance
# Reference input instance

# run calculations

# Output instance + display

# if command exit issued -> leave (case switch on input)

# dec reference
# The ‘@atexit.register’ decorator is used to call the function when the program is exiting. 
# A function with the same name but different behavior with respect to the type of argument is a generic function.  The ‘@singledispatch’ decorator 