""" 
Input_Reference Class

"""

import glob
import sys
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
        E.g. NIFC archived perimeters, CAL FIRE incidents, etc.
    
    """
    
    # AGENCY - these map to specific read types
    REFERENCE_PREDEFINED_SETS = ["nifc_interagency_history_local", 
                                 "nifc_arcgis_current_incidents",
                                 "nifc_arcgis_current_incidents_wfigs",
                                 "nifc_arcgis_2023_latest",
                                 "calfire_arcgis_historic",  
                                 "none"]
    # CONTROL - custom will need to provide their own read types
    CONTROL_TYPE = ["defined", "custom"]
    # READ TYPE - function map; if agency not specific, then must be custom set
    READ_TYPE = {  
                    "shp_local": __set_polygon_shp_local,
                    "raster_local": __set_polygon_set_raster_local,
                    "arc_gis_online": __set_polygon_arcgis_online,
                    "s3": __set_polygon_s3,
                    "other": None
                }
    
    # PREDEFINED AGENCY URLS - map mul dict entries?
    URL_MAPS = { 
            "nifc_interagency_history_local": ["/projects/shared-buckets/ksharonin/InterAgencyFirePerimeterHistory", "shp_local"],
             "nifc_arcgis_current_incidents": "https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/WFIGS_Incident_Locations_Current/FeatureServer",
            "nifc_arcgis_current_incidents_wfigs" : "https://data-nifc.opendata.arcgis.com/datasets/nifc::wfigs-current-interagency-fire-perimeters/explore?location=-0.000000%2C0.000000%2C2.51",
            "nifc_arcgis_2023_latest" : "https://data-nifc.opendata.arcgis.com/maps/2023-wildland-fire-incident-locations-to-date",
            "calfire_arcgis_historic": "https://calfire-forestry.maps.arcgis.com/apps/mapviewer/index.html?layers=e3802d2abf8741a187e73a9db49d68fe"
            }
    
    # instance initiation
    def __init__(self, title="none", 
                 usr_start: str,
                 usr_stop: str,
                 usr_bbox: list,
                 control_type="defined",
                 custom_url="none",
                 custom_read_type="none",
                 custom_filter=False,
                ):
        
        # USER INPUT / FILTERS
        self._title = title
        self._usr_start = usr_start
        self._usr_stop = usr_stop
        self._usr_bbox = usr_bbox
        self._control_type = control_type
        self._custom_url = custom_url
        self._custom_read_type = custom_read_type
        self._custom_filter = custom_filter
        
        # PROGRAM SET
        self._ds_bbox = None
        self._crs = None
        self._units = None
        self._ds_start = None
        self._ds_stop = None
        self._polygons = None
        self._ds_url = None
        self._ds_read_type = None
        
        # single setup
        self.__set_up_master()
            
            
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
    
    
    # MASTER SET UP FUNCTION
    def __set_up_master(self):
        """ set up instance properties; depends if defined or custom access """
        assert self._title in InputReference.REFERENCE_PREDEFINED_SETS, f"Provided title {self._title} is not defined."
        
        # if agency defined then use predefined dict, otherwise use user inputs
        if self._title != "none" and self._control_type == "defined":
            # set url and read type 
            assert self._tile in InputReference.URL_MAPS.keys(), f"Provided title {self._title} is not mapped to a known source URL."
            self._ds_url = URL_MAPS[self._title][0]
            self._ds_read_type = URL_MAPS[self._title][1]
            
        else:
            # set url and read type
            assert self._control_type == "custom", "Fatal: control_type not set as custom despite a none agency."
            assert self._custom_url != "none", "'none' provided as url; please provide a url for custom reading access"
            assert self._custom_read_type in InputReference.READ_TYPE.keys(), f"Invalid read type {self._custom_read_type} provided for custom input" 
            self._ds_url = self._custom_url
            self._ds_read_type = self._custom_read_type
            
        # polygon set up
        self.__dispatch_set_polygons()
        
        return self
            
            
    # SET UP HELPERS
    def __dispatch_set_polygons(self):
        """ dispatch function for """
        
        if self._ds_read_type in InputReference.READ_TYPE.keys():
            custom_set_func = InputReference.READ_TYPE[self._ds_read_type]
            custom_set_func(self)
        else:
            logging.error(f"Fatal: No function mapping defined for read type: {self._ds_read_type}")
            sys.exit()
        return self
        
    def __set_polygon_shp_local(self):
        """ given a shp locally based in mapp, set up gpd read polygons into self._polygons
            if not custom/agency defined, then preset filters will be applied
            users are welcome to modify/remove filters at their own discretion
        """
        # read in set
        df = gpd.read_file(self._ds_url)
        
        # TODO: REWORK THE BELOW EXPERIMENTAL SEQUENCE! This is specific to nifc interagency
        non_empty = df[df.geometry != None]
        non_null = non_empty[non_empty.GIS_ACRES != 0]
        finalized_perims = non_null
        finalized_perims.set_crs(PerimConsts.default_crs)
        assert finalized_williams.crs == finalized_perims.crs, "CRS mismatch"
        assert finalized_williams.crs.axis_info[0].unit_name == PerimConsts.unit_preference, f"finalized_williams fails unit check for: {PerimConsts.unit_preference}, current units: {finalized_williams.crs.axis_info[0].unit_name}"
        assert finalized_perims.crs.axis_info[0].unit_name == PerimConsts.unit_preference, f"finalized_perims fails unit check for: {PerimConsts.unit_preference}"
        extracted_year = max_timestamp.year # some kind of extraction
        try:
            extracted_year
            year_perims = finalized_perims[finalized_perims.FIRE_YEAR == str(extracted_year)]
        except NameError:
            print('WARNING: No year extracted from FEDS output. Setting to None. No year reduction applied.')
            extracted_year = None 
            year_perims = finalized_perims
            assert 1==0, "force stop -> make algorithm rely on year? otherwise doesnt seem efficient"
        # root out none types
        year_perims['DATE_NOT_NONE'] = year_perims.apply(lambda row : getattr(row, PerimConsts.date_column) is not None, axis = 1)
        year_perims = year_perims[year_perims.DATE_NOT_NONE == True]
        # root out long-len date instances
        # @TODO: origin of these dates? just wrong user control? way to salvage them reliably?
        try:
            year_perims['DATE_LEN_VALID'] = year_perims.apply(lambda row : len(getattr(row, PerimConsts.date_column)) == 8 , axis = 1)
            year_perims = year_perims[year_perims.DATE_LEN_VALID == True]
        except TypeError as e: 
            # if none detected, missed by filtering - check non existence
            print('Invalid type passed for lenght validation; check for Nones in set')
            
        # transform NIFC str to new datetime object
        cur_format = '%Y%m%d' 
        year_perims['DATE_CUR_STAMP'] =  year_perims.apply(lambda row : datetime.strptime(getattr(row, PerimConsts.date_column), cur_format), axis = 1)

        # next: pass off to comparison_pairs array
        
        
        return self
    
    # TODO
    def __set_polygon_set_raster_local(self):
        return self
    
    def __set_polygon_arcgis_online(self):
        return self
    
    def __set_polygon_s3(self):
        return self
    
    
    # NIFC PREDEFINED DATA PROCESSING
    def nifc_local_filters(self):
        return 0
    
    def nifc_arcgis_filters(self):
        return 0
    
    
    # CALFIRE DATA PROCESSING
    def calfire_local_filters(self):
        return 0
    
    def calfire_arcgis_filters(self):
        return 0
    
    # based on custom usr input; enable ability to directly pass code?
    def custom_filters_usr(self):
        return 0