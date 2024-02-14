""" 
Input_Reference Class

"""

import os
import glob
import sys
import logging
import requests
import pandas as pd
import geopandas as gpd
import fsspec

from pyproj import CRS
from owslib.ogcapi.features import Features
import geopandas as gpd
import datetime
from datetime import timedelta
from functools import singledispatch
from botocore.config import Config


pd.set_option('display.max_columns',None)

class InputReference():
    """ InputReference
        Object representing an input polygon that is compared to a FEDS object
        E.g. NIFC archived perimeters, CAL FIRE incidents, etc.
    
    """
    
    # AGENCY - these map to specific read types
    REFERENCE_PREDEFINED_SETS = [ "InterAgencyFirePerimeterHistory_All_Years_View",
                                 "Downloaded_InterAgencyFirePerimeterHistory_All_Years_View",
                                 "WFIGS_current_interagency_fire_perimeters",
                                 "california_fire_perimeters_all",
                                 "Historic_GeoMAC_Perimeters_2018",
                                 "Historic_GeoMAC_Perimeters_2019",
                                 "none"]
    # CONTROL - custom will need to provide their own read types
    CONTROL_TYPE = ["defined", "custom"]
    
    # PREDEFINED AGENCY URLS
    URL_MAPS = { 
        "InterAgencyFirePerimeterHistory_All_Years_View": ["https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/InterAgencyFirePerimeterHistory_All_Years_View/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson", "arc_gis_online"],
        "Downloaded_InterAgencyFirePerimeterHistory_All_Years_View": ["/projects/shared-buckets/ksharonin/Latest_Interagency_Fire_Perimeters", "shp_local", 's3://maap-ops-workspace/shared/ksharonin/Latest_Interagency_Fire_Perimeters/Latest_Interagency_Fire_Perimeters.json'],
        # "WFIGS_Interagency_Fire_Perimeters": [ "https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/WFIGS_Interagency_Perimeters/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson", "arc_gis_online"],
            "WFIGS_current_interagency_fire_perimeters" : ["https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/WFIGS_Interagency_Perimeters_Current/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson" , "arc_gis_online"],
            # "current_wildland_fire_incident_locations" :[ "https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/WFIGS_Incident_Locations_Current/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson", "arc_gis_online"],
            "california_fire_perimeters_all": [ "https://services1.arcgis.com/jUJYIo9tSA7EHvfZ/arcgis/rest/services/California_Fire_Perimeters/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson", "arc_gis_online"],
            "Historic_GeoMAC_Perimeters_2018": ["https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/Historic_Geomac_Perimeters_2018/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson", "arc_gis_online"],
            "Historic_GeoMAC_Perimeters_2019": ["https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/Historic_GeoMAC_Perimeters_2019/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson", "arc_gis_online"]
            }
    
    # instance initiation
    def __init__(self, 
                 usr_start: str,
                 usr_stop: str,
                 usr_bbox: list,
                 crs: int,
                 title: str ="none", 
                 control_type: str ="defined",
                 custom_url: str ="none",
                 custom_read_type: str ="none",
                 custom_col_assign: dict = {},
                 custom_filter: bool = False,
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
        self._custom_col_assign = custom_col_assign
        self._crs = CRS.from_user_input(crs)
        self._units = self._crs.axis_info[0].unit_name
        
        # PROGRAM SET
        self._ds_bbox = None
        self._units = None
        self._ds_start = None
        self._ds_stop = None
        self._polygons = None
        self._ds_url = None
        self._ds_read_type = None
        
        # SINGLE SETUP
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
        assert self._title in InputReference.REFERENCE_PREDEFINED_SETS, f"Provided title {self._title} is not defined. Current list: {InputReference.REFERENCE_PREDEFINED_SETS}"
        
        # if agency defined then use predefined dict, otherwise use user inputs
        if self._title != "none" and self._control_type == "defined":
            # set url and read type 
            assert self._title in InputReference.URL_MAPS.keys(), f"Provided title {self._title} is not mapped to a known source URL."
            self._ds_url = InputReference.URL_MAPS[self._title][0]
            self._ds_read_type = InputReference.URL_MAPS[self._title][1]
            
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
        """ dispatch function for all polygon settings"""
        
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
        try:
            df = gpd.read_file(self._ds_url)
        except Exception as e:
            pass
        try:
            fs = fsspec.filesystem("s3")
            with fs.open(InputReference.URL_MAPS[self._title][2]) as f:
                df = gpd.GeoDataFrame.from_file(f)
            
            # df = gpd.read_file(InputReference.URL_MAPS[self._title][2], config=config)
        except IOError as io_err:
            logging.error(f"ERR: unable to read local shp from url: {self._ds_url} and {InputReference.URL_MAPS[self._title][2]}, produced error: {io_err}")
            sys.exit()
        
        # filter based on predfined conds 
        if self._title == "Downloaded_InterAgencyFirePerimeterHistory_All_Years_View" or self._title == "InterAgencyFirePerimeterHistory_All_Years_View":
            df = self.filter_nifc_interagency_history_local(df)
        elif self._title == "WFIGS_current_interagency_fire_perimeters":
            df = self.filter_WFIGS_current_interagency_fire_perimeters(df)
        elif self._title == "california_fire_perimeters_all":
            df = self.filter_california_fire_perimeters_all(df)
        elif self._title.startswith("Historic_GeoMAC_Perimeters_"):
            df = self.filter_geomac(df)
        elif self._title == "" or self._title == "custom" or self._title == "Custom" or self._title == "none" or self._title == "None":
            df = self.filter_custom_local(df)
        else:
            raise ValueError("Unrecognized title input provided, see README documentation for valid title inputs")

        self._polygons = df
        
        return self
    
    
    def __set_polygon_arcgis_online(self):
        """ given geojson url, save locally as shp file into the data dir of the repo 
            set polygon attribute
        """
        
        # relative path to data dir
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(script_dir, "data")
        location = os.path.join(data_dir, f"{self._title}.geojson")
        
        geojson_url = self._ds_url
        response = requests.get(geojson_url)
        
        if response.status_code == 200:
            with open(location, "wb") as geojson_file:
                geojson_file.write(response.content)
            logging.info(f"GeoJSON data downloaded and saved to {location}")
        else:
            logging.error(f"Failed to retrieve data. Status code: {response.status_code}")
            sys.exit()
        
        gdf = gpd.read_file(location)
        
        # manually move filtering due to bug
        df_date = datetime.datetime.fromisoformat(self._usr_start)
        df_year = df_date.year
        df = gdf.set_crs(self._crs, allow_override=True)
        df = gdf.to_crs(self._crs)
        
        # condition based on custom time col
        # TODO: improve handling by making a special dict mapping for arcgis cases
        if self._title == "WFIGS_current_interagency_fire_perimeters":
            gdf['is_valid_geometry'] = gdf['geometry'].is_valid
            gdf = gdf[gdf['is_valid_geometry'] == True]
            gdf = gdf[gdf.geometry != None]
            gdf['DATE_NOT_NONE'] = gdf.apply(lambda row : getattr(row, 'poly_PolygonDateTime') is not None, axis = 1)
            gdf = gdf[gdf.DATE_NOT_NONE == True]
            gdf = gdf.dropna(subset=['poly_PolygonDateTime'])
            gdf['DATE_CUR_STAMP'] =  gdf.apply(lambda row :  datetime.datetime.fromtimestamp(getattr(row, 'poly_PolygonDateTime') / 1000.0), axis = 1)
            # outcast non matches in year self._usr_start
            gdf = gdf[gdf.DATE_CUR_STAMP.dt.year == int(self._usr_start[:4])]
        
        elif self._title == "california_fire_perimeters_all":
            gdf['is_valid_geometry'] = gdf['geometry'].is_valid
            gdf = gdf[gdf['is_valid_geometry'] == True]
            gdf['DATE_NOT_NONE'] = gdf.apply(lambda row : getattr(row, 'ALARM_DATE') is not None, axis = 1)
            gdf = gdf[gdf.DATE_NOT_NONE == True]
            gdf = gdf.dropna(subset=['ALARM_DATE'])
            gdf['DATE_CUR_STAMP'] =  gdf.apply(lambda row :  datetime.datetime.fromtimestamp(getattr(row, 'ALARM_DATE') / 1000.0), axis = 1)
            # outcast non matches in year self._usr_start
            gdf = gdf[gdf.DATE_CUR_STAMP.dt.year == int(self._usr_start[:4])]
            gdf = gdf.to_crs(self._crs)
        
        elif self._title == "WFIGS_Interagency_Fire_Perimeters":
            gdf['is_valid_geometry'] = gdf['geometry'].is_valid
            gdf = gdf[gdf['is_valid_geometry'] == True]
            # gdf['DATE_NOT_NONE'] = gdf.apply(lambda row : getattr(row, 'DATE_CUR') is not None, axis = 1)
            gdf['DATE_NOT_NONE'] = gdf.apply(lambda row : getattr(row, 'poly_PolygonDateTime') is not None, axis = 1)
            gdf = gdf[gdf.DATE_NOT_NONE == True]
            # cur_format = '%Y%m%d' 
            # gdf['DATE_CUR_STAMP'] = gdf.apply(lambda row : datetime.strptime(row.DATE_CUR, cur_format), axis = 1)
            gdf['DATE_NOT_NONE'] = gdf.apply(lambda row : getattr(row, 'poly_PolygonDateTime') is not None, axis = 1)
            gdf = gdf.dropna(subset=['poly_PolygonDateTime'])
            gdf['DATE_CUR_STAMP'] =  gdf.apply(lambda row : datetime.fromtimestamp(getattr(row, 'poly_PolygonDateTime') / 1000.0), axis = 1)
            # gdf = gdf.set_crs(self._crs, allow_override=True)
            
            gdf = gdf[gdf.DATE_CUR_STAMP.dt.year == int(self._usr_start[:4])]
            
            gdf = gdf.to_crs(self._crs)
        
        elif self._title == "InterAgencyFirePerimeterHistory_All_Years_View":
            df_date = datetime.datetime.fromisoformat(self._usr_start)
            df_start_year = df_date.year
            df_date = datetime.datetime.fromisoformat(self._usr_stop)
            df_stop_year = df_date.year

            nifc_date_format = '%Y%m%d' 

            gdf = gdf[gdf.geometry != None]
            gdf = gdf[gdf.GIS_ACRES != 0]
            gdf = gdf.set_crs(self._crs, allow_override=True)

            assert gdf.shape[0] != 0, "Invalid shape identified in ArcGIS API read"

            gdf['DATE_NOT_NONE'] = gdf.apply(lambda row : getattr(row, 'DATE_CUR') is not None, axis = 1)
            gdf = gdf[gdf.DATE_NOT_NONE == True]
            gdf['DATE_LEN_VALID'] = gdf.apply(lambda row : len(getattr(row, 'DATE_CUR')) == 8 , axis = 1)
            gdf = gdf[gdf.DATE_LEN_VALID == True]
            gdf['DATE_CUR_STAMP'] =  gdf.apply(lambda row : datetime.datetime.strptime(getattr(row, 'DATE_CUR'), nifc_date_format), axis = 1)
            gdf = gdf[gdf.DATE_CUR_STAMP.dt.year == int(self._usr_start[:4])]
            
        elif self._title.startswith("Historic_GeoMAC_Perimeters_"):
            # assume same timestamp format as WFIGS
            gdf['is_valid_geometry'] = gdf['geometry'].is_valid
            gdf = gdf[gdf['is_valid_geometry'] == True]
            gdf = gdf[gdf.geometry != None]
            gdf['DATE_NOT_NONE'] = gdf.apply(lambda row : getattr(row, 'perimeterdatetime') is not None, axis = 1)
            gdf = gdf[gdf.DATE_NOT_NONE == True]
            gdf = gdf.dropna(subset=['perimeterdatetime'])
            gdf['DATE_CUR_STAMP'] =  gdf.apply(lambda row :  datetime.datetime.fromtimestamp(getattr(row, 'perimeterdatetime') / 1000.0), axis = 1)
            # outcast non matches in year self._usr_start
            gdf = gdf[gdf.DATE_CUR_STAMP.dt.year == int(self._usr_start[:4])]
            
            gdf = gdf.set_crs(self._crs, allow_override=True)
            # gdf = gdf.to_crs(self._crs)
        
        gdf['index'] = gdf.index
        
        self._polygons = gdf
    
        return self
    
    # READ TYPE - function map; if agency not specific, then must be custom set
    READ_TYPE = {  
                    "shp_local": __set_polygon_shp_local,
                    # "raster_local": __set_polygon_set_raster_local,
                    "arc_gis_online": __set_polygon_arcgis_online,
                    # "s3": __set_polygon_s3,
                    "other": None
                }
    
    # PREDEFINED DS FILTER FUNCTIONS 
    
    # CUSTOM
    def filter_custom_local(self, df):
        """ set proper columns from user df
            return with failure if key columns missing along with
            generic errors
            
            note: does not mandate presence of incident name
        """
        assert bool(self._custom_col_assign), "Fatal: no column mapping provided; see README documentation for required column mapping for custom local dataset" 
        assert "time" in self._custom_col_assign, "Fatal: no time column detected for custom local dataset"
        assert "time_format" in self._custom_col_assign, "Fatal: no time format detected for custom local dataset"
        
        t_format = self._custom_col_assign["time_format"]
        df_date = datetime.datetime.fromisoformat(self._usr_start)
        df_year = df_date.year
        
        # crs management
        df = gdf.set_crs(self._crs, allow_override=True)
        df = gdf.to_crs(self._crs)
        
        # geom validity
        df['is_valid_geometry'] = df['geometry'].is_valid
        df = gdf[df['is_valid_geometry'] == True]
        df = gdf[df.geometry != None]
        
        # time parse + mapping
        time_col_name = self._custom_col_assign["time"]
        df['DATE_NOT_NONE'] = df.apply(lambda row : getattr(row, time_col_name) is not None, axis = 1)
        df = df[df.DATE_NOT_NONE == True]
        # check type is str passed, cannot apply operation on datetime objects
        assert type(df.iloc[0][time_col_name]) is str, "Fatal: time column not in string form, see README documentation for proper column requirements"
        df['DATE_CUR_STAMP'] =  df.apply(lambda row : datetime.datetime.strptime(getattr(row, time_col_name), t_format), axis = 1)
        
        # outcast non matches in year self._usr_start
        df = df[df.DATE_CUR_STAMP.dt.year == int(self._usr_start[:4])]
        
        df['index'] = df.index
        
        # if incident name present, assign to designated term
        if "incident_name" in self._custom_col_assign:
            df['INCIDENT'] = df[self._custom_col_assign["incident_name"]]
        
        return df
    
    # NIFC 
    def filter_nifc_interagency_history_local(self, df):
        """ filter a passed polygon set under known nifc experimental properties & adds new cols
            actions:
            - remove None geometries
            - remove entries w/ 0 acres
            - set crs to passed crs
            - set exact year
            - flag and remove any none dates
            - flag and remove improper length date cols
            - generate datetime object from date
        """
        
        # fetch dates
        df_date = datetime.datetime.fromisoformat(self._usr_start)
        df_start_year = df_date.year
        df_date = datetime.datetime.fromisoformat(self._usr_stop)
        df_stop_year = df_date.year
            
        nifc_date_format = '%Y%m%d' 
        
        # actions as docstring specifies
        df = df[df.geometry != None]
        df = df[df.GIS_ACRES != 0]
        df = df.set_crs(self._crs, allow_override=True)    
        
        if df.shape[0] == 0:
            assert 1 == 0, "Not possible"
            sys.exit()
        
        df['DATE_NOT_NONE'] = df.apply(lambda row : getattr(row, 'DATE_CUR') is not None, axis = 1)
        df = df[df.DATE_NOT_NONE == True]
        df['DATE_LEN_VALID'] = df.apply(lambda row : len(getattr(row, 'DATE_CUR')) == 8 , axis = 1)
        df = df[df.DATE_LEN_VALID == True]
        df['DATE_CUR_STAMP'] =  df.apply(lambda row : datetime.datetime.strptime(getattr(row, 'DATE_CUR'), nifc_date_format), axis = 1)
        # outcast non matches in year self._usr_start
        df = df[df.DATE_CUR_STAMP.dt.year == int(self._usr_start[:4])]
        
        df['index'] = df.index
        
        return df
    
    def filter_WFIGS_current_interagency_fire_perimeters(self, df):
        """ predefined filter for the WFIGS_current_interagency_fire_perimeters set
            - generate 'DATE_CUR_STAMP' col
            - set crs
            - remove none dates
        
        """
        df_date = datetime.fromisoformat(self._usr_start)
        df_year = df_date.year
        df = df.set_crs(self._crs, allow_override=True)
        
        df['DATE_NOT_NONE'] = df.apply(lambda row : getattr(row, 'poly_PolygonDateTime') is not None, axis = 1)
        df = df[df.DATE_NOT_NONE == True]
        df['DATE_CUR_STAMP'] =  df.apply(lambda row :  datetime.datetime.fromtimestamp(getattr(row, 'poly_PolygonDateTime') / 1000.0), axis = 1)
        # outcast non matches in year self._usr_start
        df = df[df.DATE_CUR_STAMP.dt.year == int(self._usr_start[:4])]  
        
        return df
    
    def filter_geomac(self, df):
        """ predefined filter for the GeoMAC sets
            - generate 'DATE_CUR_STAMP' col - assume 'perimeterdatetime' used
            - set crs
            - remove none dates
        
        """
        
        df_date = datetime.fromisoformat(self._usr_start)
        df_year = df_date.year
        df = df.set_crs(self._crs, allow_override=True)
        
        df['DATE_NOT_NONE'] = df.apply(lambda row : getattr(row, 'perimeterdatetime') is not None, axis = 1)
        df = df[df.DATE_NOT_NONE == True]
        df['DATE_CUR_STAMP'] =  df.apply(lambda row :  datetime.datetime.fromtimestamp(getattr(row, 'perimeterdatetime') / 1000.0), axis = 1)
        # outcast non matches in year self._usr_start
        df = df[df.DATE_CUR_STAMP.dt.year == int(self._usr_start[:4])]  
        
        return df
