""" 
Output_Calculation Class

"""

import glob
import sys
import logging
import pandas as pd
import geopandas as gpd
import fsspec
import boto3
import geopandas as gpd
import datetime as dt
import logging
import csv
import rasterio
import matplotlib.pyplot as plt

from tqdm import tqdm
from pyproj import CRS
from owslib.ogcapi.features import Features
from datetime import datetime, timedelta
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, EndpointConnectionError

# class imports
import Utilities
from Input_Reference import InputReference
from Input_FEDS import InputFEDS

class OutputCalculation():
    
    """ OutputCalculation
        Class representing output calculation of feds_input vs ref_input
    """
    
    # implemented output formats
    OUTPUT_FORMATS = ["csv"]
    
    def __init__(self, 
                 feds_input: InputFEDS, 
                 ref_input: InputReference, 
                 output_format: str, 
                 output_maap_url: str,
                 day_search_range: int,
                 print_on: bool,
                 plot_on: bool):

        # USER INPUT / FILTERS
        self._feds_input = feds_input
        self._ref_input = ref_input
        self._output_format = output_format
        self._output_maap_url = output_maap_url
        self._day_search_range = day_search_range
        self._print_on = print_on
        self._plot_on = plot_on
        
        # PROGRAM SET
        self._polygons = None
        self._calculations = None 
        self._s3_url = None
        
        # SINGLE SETUP
        self.__set_up_master()
        
    @property
    def feds_input(self):
        return self._feds_input
    
    @property
    def ref_input(self):
        return self._ref_input
    
    @property
    def polygons(self):
        return self._polygons
    
    # MASTER SET UP FUNCTION
    def __set_up_master(self):
        """ set up outputcalc instance with checks and generations; run main calculations"""
        
        assert self._output_format in OutputCalculation.OUTPUT_FORMATS, f"Provided output format {self._output_format} is NOT VALID, select only from implemented formats: {OutputCalculation.OUTPUT_FORMATS}"
        assert self.__set_up_valid_maap_url, f"Invalid URL: see assertions and/or possibly missing s3://maap-ops-workspace/shared/ in url. Provided url: {self._output_maap_url}"
        assert self._day_search_range >= 0, f"Invalid provided day range {self._day_search_range}. Must be x >= 0"
        assert self._feds_input.crs == self._ref_input.crs, f"Mismatching CRS for FEDS and reference; must correct before continuing: feds: {self._feds_input.crs} vs ref: {self._ref_input.crs}"
        
        # run calculations
        self.__run_calculations() # --> internally finds best matches and runs on the best matches
        
        if self._print_on:
            self.__print_output()
        if self._plot_on:
            self.__plot_output()
          
        # write to csv
        self.write_to_csv()
        
        return self
    
    def __set_up_valid_maap_url(self):
        """ given a maap-ops-workspace url, check if valid with naming + s3 access"""
        
        maap_ops_contained ="s3://maap-ops-workspace/shared/" in self._output_maap_url
        s3_url = self._output_maap_url 
        
        try:
            s3 = boto3.client('s3')
            bucket, key, nested = Utilities.split_s3_path(s3_url)

            if nested:
                # iter and locate bucket
                assert len(bucket) == 2, "FATAL: bucket + prefix design should only be len2"
                response = s3.list_objects_v2(Bucket=bucket[0], Prefix=bucket[1])
                folders = set(object['Key'][:object['Key'].rfind('/')+1] for object in response['Contents'] if '/' in object['Key'])
                if bucket[1] in folders: 
                    return True and maap_ops_contained
                else:
                    logging.error(f"ERR: prefix {bucket[1]} not located; invalid url passed {self._output_maap_url}")
                    return False
            else:
                s3 = boto3.resource('s3')
                obj = s3.Bucket(bucket)
            
                if bucket_obj.creation_date:
                    return True and maap_ops_contained
                else:
                    return False
        
        except NoCredentialsError:
            print("AWS credentials not found. Please configure your AWS credentials.")
        except PartialCredentialsError:
            print("Incomplete AWS credentials found.")
        except EndpointConnectionError:
            print("Could not connect to the AWS endpoint. Please check your AWS configuration.")
        except Exception as e:
            print(f"Error: {str(e)}")

        return False
    
    def __run_calculations(self):
        """ orchestrate all calculations; either return back to enable output write or write here"""
        # feds polygon index mapping to reference index of closest type (or None)
        index_pairs = OutputCalculation.closest_date_match(self)
        
        calculations = { 'index_pairs': index_pairs,
                         'ratio': [],
                         'accuracy': [],
                         'precision': [],
                         'recall': [],
                         'iou': [],
                         'f1': [],
                         'symm_ratio': []
                       }
                                 
        for feds_ref_pair in index_pairs: # e.g. (4, 1) <- feds index 4 best matches with ref poly at index 1
                                 
            skip_first_key = True
                                 
            # no reference polygon --> attach none to tracked calculations
            if (feds_ref_pair[1] is None):
                for key in calculations:
                    if skip_first_key:
                        skip_first_key = False
                        continue  # Skip the first key
                    calculations[key].append(None)
                continue
           
            # fetch corresponding polygons
            feds_poly = self._feds_input.polygons[self._feds_input.polygons['index'] == feds_ref_pair[0]]
            ref_poly = self._ref_input.polygons[self._ref_input.polygons['index'] == feds_ref_pair[1]]
               
            # run through calculations
            ratio = OutputCalculation.ratioCalculation(feds_poly, ref_poly)
            accuracy = OutputCalculation.accuracyCalculation(feds_poly, ref_poly)
            precision = OutputCalculation.precisionCalculation(feds_poly, ref_poly)
            recall = OutputCalculation.recallCalculation(feds_poly, ref_poly)
            iou= OutputCalculation.IOUCalculation(feds_poly, ref_poly)
            f1 = OutputCalculation.f1ScoreCalculation(feds_poly, ref_poly) 
            symm_ratio = OutputCalculation.symmDiffRatioCalculation(feds_poly, ref_poly) # indep calc
            
            # add to tracking arr                    
            calculations['ratio'].append(ratio)
            calculations['accuracy'].append(accuracy)
            calculations['precision'].append(precision)
            calculations['recall'].append(recall)
            calculations['iou'].append(iou)
            calculations['f1'].append(f1)
            calculations['symm_ratio'].append(symm_ratio)
            
        # verify same sizing
        for key in calculations: 
            assert len(calculations[key]) == len(index_pairs), f"FATAL: mismatching sizing of arr at key {key} for calculations"
        
        # persist calcs in dict form
        self._calculations = calculations
        logging.info('Calculations complete!')
        
        return self
                                 
    def __print_output(self):
        """ print output using the _calculations var"""
                                 
        calculations = self._calculations
        
        for i in range(len(calculations['index_pairs'])):
            skip_first_key = True
            # per each --> print value at corresponding i index
            vals = []
            for key in calculations:
                if skip_first_key:
                    skip_first_key = False
                    continue  # Skip the first key
                vals.append(calculations[key][i])
            
            # skip if none result, too verbose if all displayed
            if all(value is None for value in vals):
                print(f'NO CALCULATION RESULTS, SKIP FEDS INDEX {calculations["index_pairs"][i][0]} & REFERENCE INDEX {calculations["index_pairs"][i][0]}')
            else: 
                print(f'CALCULATED A RESULT: POLYGON FEDS AT INDEX {calculations["index_pairs"][i][0]} AGAINST REFERENCE POLYGON AT INDEX {calculations["index_pairs"][i][1]}:')
                print(f'Ratio: {vals[0]}, Accuracy: {vals[1]}, Precision: {vals[2]}, Recall: {vals[3]}, IOU: {vals[4]}, F1 {vals[5]}, Symmetric Ratio: {vals[6]}')
                print(f'All measurements in units {self._feds_input.polygons.crs.axis_info[0].unit_name}')

        return self
    
    def __plot_output(self):
        """ generate plots for all successful (non-None) indices
            include metadata relevant to project
            
            each match pair == separate plot image
        """
        print("\n")
        print("PLOTTING ON: BEGIN PLOT OUTPUT")
        
        # fetch dict vals
        calculations = self._calculations
        
        # poly + time fetch
        feds_polygons = self._feds_input.polygons
        ref_polygons = self._ref_input.polygons
        
        # TODO generate series of plots for all non-None results
        for pair in calculations['index_pairs']:
            # coresponding index
            i = calculations['index_pairs'].index(pair)
            # ignore none value results
            if all( value is None for value in 
                    [
                        calculations['ratio'][i],
                        calculations['accuracy'][i],
                        calculations['precision'][i],
                        calculations['recall'][i],
                        calculations['iou'][i],
                        calculations['f1'][i],
                        calculations['symm_ratio'][i]
                    ]
                ):
                    continue
            
            # poly + time extraction
            feds_poly = feds_polygons[feds_polygons['index'] == calculations['index_pairs'][i][0]]
            ref_poly = ref_polygons[ref_polygons['index'] == calculations['index_pairs'][i][1]]
            feds_time = feds_poly.t.values[0]
            ref_time = ref_poly['DATE_CUR_STAMP'].values[0]
        
            # apply indices
            index1, index2 = pair
            feds_poly = feds_polygons[feds_polygons['index'] == index1]
            ref_poly = ref_polygons[ref_polygons['index'] == index2]

            # new fig per pair
            fig, ax = plt.subplots(figsize=(15, 15))
            feds_plot = feds_poly.plot(ax=ax, color="red",edgecolor="black", linewidth=1.5, label="FEDS Fire Estimate")
            ref_plot = ref_poly.plot(ax=ax, color="gold", edgecolor="black", linewidth=1.5, hatch='\\', alpha=0.7, label="Reference Nearest Date + Intersection")
            
            # ax.legend(handles=[feds_plot, ref_plot])
            
            # show plot
            ax.set_title(f"FEDS ({index1}) at {feds_time} VS. Ref ({index2}) at {ref_time}", fontsize=17)
            ax.set_xlabel("Longitude", fontsize=14)
            ax.set_ylabel("Latitude", fontsize=14)
            plt.grid(True)
            plt.show()
        
        print("PLOTTING COMPLETE")
    
    def __set_up_output_maap_file(self):
        """ with a valid maap-ops-workspace url (bucket + key) --> make an object in the bucket with prefix; rechecks access should any edge cases occur (e.g. aws going down/skipping)"""
        
        # test out bucket access and put in object if available
        # s3_url = self._output_maap_url 
                                 
        # TODO: into nested bucket
        # s3.put_object(
            # Bucket=buckey,
            # Key=key+'.'+{self._output_format} # since only name is passed, must add on prefix
        # )
                                 
        return self
    
    def export_polygons(self, polygons, path: str):
        """ export polygons to designated paths by user
            let this be a public access method for the 
            sake of not re-inventing vars
        """
        polygons.to_file(path)
        print(f"Export complete to path: {path}")
        
        return
    
    
    # GENERAL PROCESSING METHODS
                                 
    def get_nearest_by_date(dataset, timestamp, dayrange: int):
        """ Identify rows of dataset with timestamp matches;
        
            expects year, month, date in datetime format
                dataset: input dataset to search for closest match
                timestamp: timestamp we want a close match for
                
            returns: dataset with d->m->y closest matches
        """

        # timestamp = timestamp.item()
        transformed = dataset.DATE_CUR_STAMP.tolist()
        clos_dict = {
          abs(timestamp.timestamp() - date.timestamp()) : date
          for date in transformed
        }

        res = clos_dict[min(clos_dict.keys())]

        # check on dayrange flexibility - trigger outer exception if failing
        if abs(timestamp.day - res.day) > dayrange and dayrange == 7:
            return None

        if not abs(timestamp.day - res.day) <= dayrange: 
            logging.error("WARNING in get_nearest_by_date: No dates found in specified range for this reference collection; try a more flexible range by adjusting `dayrange` var")
        # fetch rows with res timestamp
        finalized = dataset[dataset['DATE_CUR_STAMP'] == res]

        return finalized
                                 
                                 
    def closest_date_match(self) -> list:
        """ given the feds and reference polygons
            return list mapping the feds input to 
            closest reference polygons
        """
        
        # store as (feds_poly index, ref_polygon index)
        matches = []

        # fetch polygons
        feds_polygons = self._feds_input.polygons
        ref_polygons = self._ref_input.polygons
        
        logging.info(f'Number of total feds_polygons: {len(self._feds_input.polygons.index)}')
        logging.info(f'Number of total ref_polygons: {len(self._ref_input.polygons.index)}')
        
        total_iterations = feds_polygons.shape[0]
        
        # iterate through all feds polys
        for feds_poly_i in tqdm(range(total_iterations), desc="Running FEDS-Reference Match Algorithm", unit="polygon"):
            
            # grab feds polygon + index layout
            curr_feds_poly = feds_polygons.iloc[[feds_poly_i]]
            curr_feds_sindex = curr_feds_poly.sindex
            
            # indices of refs that intersected with this feds poly
            curr_finds = []
            
            # PHASE 1: FIND INTERSECTIONS OF ANY KIND
            for idx in range(len(ref_polygons)):
                ref_poly = ref_polygons.iloc[idx]
                tmp_bbox = ref_poly.geometry.bounds
                possible_matches_index = list(curr_feds_sindex.intersection(tmp_bbox))
                possible_matches = curr_feds_poly.iloc[possible_matches_index]
                if not possible_matches.empty:
                    intersect = gpd.overlay(ref_polygons.iloc[[idx]], possible_matches, how='intersection')
                    if not intersect.empty:
                        curr_finds.append(idx)
           
            if not len(curr_finds):
                # debug warnings
                # logging.warning(f'NO MATCHES FOUND FOR FEDS_POLYGON AT INDEX: {feds_polygons["index"].iloc[feds_poly_i]}; UNABLE TO FIND BEST DATE MATCHES, ATTACHING NONE FOR REFERENCE INDEX')
                matches.append((feds_polygons['index'].iloc[feds_poly_i], None))
                continue
            
            
            timestamp = curr_feds_poly.t # feds time stamp - 2023-09-22T12:00:00 in str format 
            set_up_finds = ref_polygons.take(curr_finds)
                                 
            # PHASE 2: GET BEST TIME STAMP SET, TEST IF INTERSECTIONS FIT THIS BEST DATE
            try:
                timestamp = datetime.strptime(timestamp.values[0], "%Y-%m-%dT%H:%M:%S")
                time_matches = OutputCalculation.get_nearest_by_date(set_up_finds, timestamp, self._day_search_range)
            except Exception as e:
                sys.stdout.write(f'Encountered error when running get_nearest_by_date: {e} \n')
                sys.stdout.flush()
                sys.stdout.write(f'DUE TO ERR: FEDS POLY WITH INDEX {feds_polygons["index"].iloc[feds_poly_i]} HAS NO INTERSECTIONS AT BEST DATES: ATTACHING NONE FOR REFERENCE INDEX \n')
                sys.stdout.flush()
                
                matches.append((feds_polygons['index'].iloc[feds_poly_i], None))
                continue
            if time_matches is None:
                sys.stdout.write(f'TIME MATCH WARNING: the intersecting pair does not have a timestamp difference within the specified day search range window: {self._day_search_range} \n')
                sys.stdout.flush()
                sys.stdout.write(f'Intersection pair will still be included for user inspection; FEDS at index {feds_poly_i} and Reference at index {curr_finds}. \n')
                sys.stdout.flush()
                
                time_matches = set_up_finds
                
            
            # PHASE 3: FLATTEN TIME MATCHES + INTERSECTING
            intersect_and_date = [time_matches.iloc[[indx]]['index'].values[0] for indx in range(time_matches.shape[0])]
            assert len(intersect_and_date) != 0, "FATAL: len 0 should not occur with the intersect + best date array"
            # if len(intersect_and_date) > 1:
            #     sys.stdout.write(f'FEDS polygon at index {feds_polygons["index"].iloc[feds_poly_i]} has MULTIPLE qualifying polygons to compare against: {len(intersect_and_date)} resulted. Select first polygon only; SUBJECT TO CHANGE! \n')
            #     sys.stdout.flush()
                
            # multi match supressor
            # [matches.append((feds_polygons['index'].iloc[feds_poly_i], a_match)) for a_match in intersect_and_date[0:1]]
            [matches.append((feds_polygons['index'].iloc[feds_poly_i], a_match)) for a_match in intersect_and_date]
            
                               
        print('DATE MATCHING COMPLETE')
        return matches
    
    def write_to_csv(self):
        """ take result calculation columns and output into csv format
            take note of instance vars:
            
            self._output_format = output_format
            self._output_maap_url = output_maap_url
            self._dump = None # content to dump into file
            
            wants cols for the feds index, reference index, then corresponding calcs
            
            e.g. for calculations = { 'index_pairs': index_pairs,
                         'ratio': [],
                         'accuracy': [],
                         'precision': [],
                         'recall': [],
                         'iou': [],
                         'f1': [],
                         'symm_ratio': []
                       }
            row i = feds index: index_pairs[i][0], 
                    ref index: index_pairs[i][1],
                    ratio: ratio[i],
                    etc.
        
        """
        
        # fetch dict 
        calculations = self._calculations
        # source length from top given all should be same len
        file_name = self._output_maap_url
        # fetch polygons to extract meta data
        feds_polygons = self._feds_input.polygons
        ref_polygons = self._ref_input.polygons
        
        with open(file_name, 'w', newline='') as csvfile:
            # erase prev content 
            csvfile.truncate()
            
            fieldnames = ['feds_index', 
                          'feds_polygon',
                          'ref_index', 
                          'ref_polygon',
                          'incident_name', # need to condition if available
                          'feds_timestamp',
                          'ref_timestamp',
                          'abs(feds-ref)_days',
                          'ratio', 
                          'accuracy', 
                          'precision', 
                          'recall', 
                          'iou', 
                          'f1', 
                          'symm_ratio']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            num_rows = len(calculations['index_pairs']) 

            for i in range(num_rows):
                # skip None values for write in
                if all( value is None for value in 
                    [
                        calculations['ratio'][i],
                        calculations['accuracy'][i],
                        calculations['precision'][i],
                        calculations['recall'][i],
                        calculations['iou'][i],
                        calculations['f1'][i],
                        calculations['symm_ratio'][i]
                    ]
                ):
                    continue
                    
                else: 
                    # poly extraction
                    feds_poly = feds_polygons[feds_polygons['index'] == calculations['index_pairs'][i][0]]
                    ref_poly = ref_polygons[ref_polygons['index'] == calculations['index_pairs'][i][1]]
                    # timestamp extract
                    feds_time = feds_poly.t.values[0]
                    ref_time = ref_poly['DATE_CUR_STAMP'].values[0]
                    
                    # print(f"DEBUG type for feds time {type(feds_time)}")
                    
                    # convert for abso
                    feds_time_int = datetime.strptime(feds_time, "%Y-%m-%dT%H:%M:%S")
                    ref_time_str = str(ref_time)
                    ref_format = "%Y-%m-%dT%H:%M:%S.%f" + ref_time_str[-3:]
                    ref_time_int = datetime.strptime(ref_time_str, ref_format)
                    
                    # ref_time_int = ref_time.astype(datetime) # datetime.strptime(ref_time, "%Y-%m-%dT%H:%M:%S")
                    # abso difference in days
                    abs_day_diff = abs((feds_time_int - ref_time_int).days)
                    
                    # UFuncTypeError: ufunc 'subtract' cannot use operands with types dtype('<U19') and dtype('<M8[ns]')
                    # suspect name match - use known pre-definedd col labels
                    if 'INCIDENT' in ref_poly.columns:
                        incident_name = ref_poly['INCIDENT'].values[0]
                    elif 'poly_IncidentName' in ref_poly.columns:
                        incident_name = ref_poly['poly_IncidentName'].values[0]
                    elif 'FIRE_NAME' in ref_poly.columns:
                        incident_name = ref_poly['FIRE_NAME'].values[0]
                    elif 'incidentname' in ref_poly.columns:
                        incident_name = ref_poly['incidentname'].values[0]
                    else:
                        incident_name = ""
                    
                    row_data = {
                        'feds_index': calculations['index_pairs'][i][0],
                        'feds_polygon': self._feds_input._polygons.loc[calculations['index_pairs'][i][0]]['geometry'].wkt,
                        'ref_index': calculations['index_pairs'][i][1],
                        'ref_polygon': self._ref_input._polygons.loc[calculations['index_pairs'][i][1]]['geometry'].wkt,
                        'incident_name': incident_name,
                        'feds_timestamp': feds_time,
                        'ref_timestamp': ref_time,
                        'abs(feds-ref)_days': abs_day_diff,
                        'ratio': calculations['ratio'][i],
                        'accuracy': calculations['accuracy'][i],
                        'precision': calculations['precision'][i],
                        'recall': calculations['recall'][i],
                        'iou': calculations['iou'][i],
                        'f1': calculations['f1'][i],
                        'symm_ratio': calculations['symm_ratio'][i]
                    }
                    writer.writerow(row_data)
        
        print("\n")
        print(f"CSV output complete! Check file {file_name} for results. NOTE: None result rows were excluded.")
        
    # TIF READING AND PROCESSING
    
    def tif_analysis(self, tif_path: str, req_calc: str, date_restrict = None):
        """ given output obj with available feds + ref polygons
            user specifies tif path (tif_path) and req_calcs (str that is
            MEAN, MEDIAN, UNIQUE)
        
        """
        
        # input checks
        valid_calc_choices = ["MEAN", "MEDIAN", "UNIQUE"]
        
        assert req_calc in valid_calc_choices, f"Provided req_calc argument is not valid, please select a choice from the following: {valid_calc_choices}"
        
        # assign main polygons
        feds_polygons = self._feds_input.polygons
        ref_polygons =self._ref_input.polygons
        indices = self._calculations['index_pairs']
        
        # correspond to indices/pairs
        mass_results = []
        
        for pair in indices:
            
            index1, index2 = pair
            
            if index2 is None:
                continue
                
            feds_inst = feds_polygons[feds_polygons['index'] == index1]
            ref_inst = ref_polygons[ref_polygons['index'] == index2]
            
            # given an int time restriction, eliminate pairs not in bounds 
            if date_restrict is not None:
                assert type(date_restrict) is int, "date_restrict must be int, as in number of days permitted for timestamp difference"
                # assert of datetime type 
                feds_time = datetime.strptime(feds_inst.t.values[0], "%Y-%m-%dT%H:%M:%S")
                is_within_time_given = OutputCalculation.get_nearest_by_date(ref_inst, feds_time, date_restrict)
                if  is_within_time_given.empty or is_within_time_given is None:
                    continue
                
            # exceeding zone for feds: feds - ref == feds exceed amount
            # diff_area = gpd.overlay(feds_inst, ref_inst, how='symmetric_difference')
            diff_area = feds_inst.symmetric_difference(ref_inst, align=False)
            
            # open and generate mask tif
            with rasterio.open(tif_path) as src:
                masked_tif, _ = mask(src, intersection_area.geometry, crop=True)
            
            # append requested val generated from usr req
            if masked_tif is not None:
                if req_calc == "MEAN":
                    avg_val = np.nanmean(masked_tif)
                    mass_results.append(avg_val)
                elif req_calc == "MEDIAN":
                    median_val = np.nanmedian(masked_tif)
                    mass_results.append(median_val)
                else:
                    unique_vals = np.unique(masked_tif)
                    mass_results.append([unique_vals])

        return mass_results
    
    #### WARNING: EXPERIMENTAL METHODS BELOW, NOT CONFORMING TO OOP DESIGN ###   
    
    def init_best_simplify(
                       calc_method, 
                       lowerPref, 
                       base_tolerance,
                      ):
        """ run simplify algorithm and return back best result
            use calc_method and control bool to indicate "direction" of best performance

            e.g. calc method symmDiffRatioCalculation(feds_poly, ref_poly)
            false since higher ratio value is better similarity
        """
        if lowerPref:
            top_performance = 100000000
        else: 
            top_performance = 0
            
        master_threshold_collection = []
        
        calculations = self._calculations
        
        # poly + time fetch
        feds_polygons = self._feds_input.polygons
        ref_polygons = self._ref_input.polygons
        
        for pair in calculations['index_pairs']:
            # coresponding index
            i = calculations['index_pairs'].index(pair)
            # ignore none value results
            if all( value is None for value in 
                    [
                        calculations['ratio'][i],
                        calculations['accuracy'][i],
                        calculations['precision'][i],
                        calculations['recall'][i],
                        calculations['iou'][i],
                        calculations['f1'][i],
                        calculations['symm_ratio'][i]
                    ]
                ):
                    continue
            
            # poly + time extraction
            # feds_poly = feds_polygons[feds_polygons['index'] == calculations['index_pairs'][i][0]]
            # ref_poly = ref_polygons[ref_polygons['index'] == calculations['index_pairs'][i][1]]
        
            # apply indices
            index1, index2 = pair
            feds_poly = feds_polygons[feds_polygons['index'] == index1]
            ref_poly = ref_polygons[ref_polygons['index'] == index2]
            

            top_tolerance = 0
            threshold = best_simplification(sat_fire, 
                                            air_fire, 
                                            top_performance, 
                                            top_tolerance,
                                            base_tolerance,
                                            calc_method,
                                            lowerPref,
                                            [],
                                            [], 
                                            []
                                           )
            
            master_threshold_collection.append(threshold)

        return master_threshold_collection
        
    def simplify_geometry(shape, tolerance):
        """ shape: to simplify
            tolerance: passed to shapely tol
            return: simplified shape
        """
        # keep preserve_topology as default (true)
        assert isinstance(shape, gpd.GeoDataFrame)
        return shape.geometry.simplify(tolerance)

    # @TODO: finish implementing recursive function on simplification calc
    def best_simplification (feds, nifc,
                             top_performance, 
                             top_tolerance, 
                             base_tolerance, 
                             calc_method, 
                             lowerPref,
                             usr_step=0.001
                             ):
        """ feds: feds source
            nifc: external source to compare to
            top_performance: best numeric value (default is worst value aka > 100 % error)
            top_tolerance: corresponding simplification with best performance
            base_tolerance: counter for tracking progress from limit -> 0
            calc_method
            lowerPref: true if a "better" score is considered a lower value

            return: top_tolerance (best tolerance value from recursion)

        """
        if base_tolerance <= 0.000000000001:
            return top_tolerance, simple_history, performance_history, tolerance_history

        # simplify + calculate performance
        simplified_feds = simplify_geometry(feds, base_tolerance)
        simple_history.append(simplified_feds)
        curr_performance = calc_method(simplified_feds, nifc)
        performance_history.append(curr_performance)
        tolerance_history.append(base_tolerance)

        # if performance "better" (depends on passed bool / method) -> persist
        if curr_performance < top_performance and lowerPref:
            top_performance = curr_performance
            top_tolerance = base_tolerance
        elif curr_performance > top_performance and not lowerPref:
            top_performance = curr_performance
            top_tolerance = base_tolerance

        # reduce and keep recursing down - STEP SUBJECT TO CHANGE
        # TODO: make user accessible 
        base_tolerance -= usr_step

        return best_simplification(feds, nifc, top_performance, top_tolerance, base_tolerance, calc_method, lowerPref, simple_history, performance_history, tolerance_history, usr_step)


    def areaCalculation(geom_instance):
        """ Calculate area of the object, including
            mult-row instances via loop
            Input: geom data frame instance
            Output: numeric area calculation (units defined in const)
            
            # terms:
            # FEDS data are considered as the predicted class. 
            # TN: True Negative; FN: False Negative; FP: False Positive; 
            # TP: True Positive; FEDS_UB: Unburned area from FEDS; 
            # FEDS_B: Area burned from FEDS; FRAP_UB: Unburned area from FRAP; 
            # FRAP_B: Burned area from FRAP; AREA_TOTAL: Total land area in CA
        """
        try:
            area = 0
            for i in range(geom_instance.geometry.area.shape[0]):
                area += geom_instance.geometry.area[i]
        except KeyError:
            # print('Identified key error in areaCalculation(): returning item() based area calc', end='\r')
            area = geom_instance.geometry.area.item()

        return area

    def truePos(feds_inst, nifc_inst):
        """ Calculate true pos area:
            where both NIFC and FEDS burned
            return basic intersection
        """
        overlay = gpd.overlay(feds_inst, nifc_inst, how='intersection')
        result = OutputCalculation.areaCalculation(overlay) # overlay.geometry.area.item()
        return result

    def falseNeg(feds_inst, nifc_inst):
        """ Calculate false negative area:
            NIFC burned but FEDS DID NOT burn (unburned needs envelope)
            make bounding -> get negative of Feds -> intersect with nifc (burning)
        """
        # union to envelope 
        unionr = gpd.overlay(feds_inst, nifc_inst, how='union')

        # generate bounding box fitting both instances (even if multi-poly)
        net_bounding = unionr.geometry.envelope
        # net_barea = areaCalculation(net_bounding)
        # convert to data frame
        net_bounding = net_bounding.to_frame()

        feds_neg = gpd.overlay(net_bounding, feds_inst, how='difference')
        result = gpd.overlay(feds_neg, nifc_inst, keep_geom_type=False, how='intersection')
        result = OutputCalculation.areaCalculation(result)

        return result

    def falsePos(feds_inst, nifc_inst):
        """ Calculate false negative area:
            NIFC DID NOT burn (unburned needs envelope) but FEDS burned 
            bounding -> get negative of nifc -> intersect with feds (burning)
        """
        # union to envelope 
        unionr = gpd.overlay(feds_inst, nifc_inst, how='union')

        # generate bounding box fitting both instances (even if multi-poly)
        net_bounding = unionr.geometry.envelope
        # net_barea = areaCalculation(net_bounding)
        # convert to data frame
        net_bounding = net_bounding.to_frame()

        nifc_neg = gpd.overlay(net_bounding, nifc_inst, how='difference')

        result = gpd.overlay(nifc_neg, feds_inst, keep_geom_type=False, how='intersection')
        result = OutputCalculation.areaCalculation(result)

        return result

    def trueNeg(feds_inst, nifc_inst):
        """ Calculate true negative area (agreeing on none geom)
            input: two geo dataframes
            output: area where both agree of no geom
        """

        # union to envelope 
        unionr = gpd.overlay(feds_inst, nifc_inst, how='union')

        # generate bounding box fitting both instances (even if multi-poly)
        net_bounding = unionr.geometry.envelope
        net_barea = OutputCalculation.areaCalculation(net_bounding)
        # convert to data frame
        net_bounding = net_bounding.to_frame()

        # subtract feds_inst and nifc_inst from bounding area
        feds_neg = gpd.overlay(net_bounding, feds_inst, how='difference')
        nifc_neg = gpd.overlay(net_bounding, nifc_inst, how='difference')

        # TN = calculate intersection of both "negatives"
        inter_neg = gpd.overlay(feds_neg, nifc_neg, keep_geom_type=False, how='intersection')
        result = OutputCalculation.areaCalculation(inter_neg)

        return result

    def areaTotal(feds_inst, nifc_inst):
        """ Calculate total Area defined in table 6:	
            FEDS_B/REF_B(burned area)
        """
        # union to envelope 
        unionr = gpd.overlay(feds_inst, nifc_inst, how='union')
        # generate bounding box fitting both instances (even if multi-poly)
        net_bounding = unionr.geometry.envelope
        net_barea = OutputCalculation.areaCalculation(net_bounding)
        # convert to data frame
        # net_bounding = net_bounding.to_frame()

        return net_barea

    def ratioCalculation(feds_inst, nifc_inst):
        """ Calculate ratio defined in table 6:	
            FEDS_B/REF_B(burned area)
        """
        # sum area (since mul entries may exist) up by calc
        feds_area = OutputCalculation.areaCalculation(feds_inst)
        nifc_area = OutputCalculation.areaCalculation(nifc_inst)

        assert feds_area is not None, "None type detected for area; something went wrong"
        assert nifc_area is not None, "None type detected for area; something went wrong"

        return feds_area / nifc_area

    def accuracyCalculation(feds_inst, nifc_inst):
        """ Calculate accuracy defined in table 6:
            (TP+TN)/AREA_TOTAL

            TN == agreed inverse by bounding box
            TP == FRAP + FEDS agree on burned (intersect)
        """
        TN = OutputCalculation.trueNeg(feds_inst, nifc_inst)
        TP = OutputCalculation.truePos(feds_inst, nifc_inst)
        AREA_TOTAL = OutputCalculation.areaTotal(feds_inst, nifc_inst)

        return (TN + TP) / AREA_TOTAL

    # @TODO: call percision calculation func
    def precisionCalculation(feds_inst, nifc_inst):
        """ TP/FEDS_B
            TP == FRAP + FEDS agree on burned (intersect)
            FEDS_B == all burned of feds 
        """
        assert isinstance(feds_inst, pd.DataFrame) and isinstance(nifc_inst, pd.DataFrame), "Object types will fail intersection calculation; check inputs"
        # calculate intersect (agreement) -> divide
        # overlay = gpd.overlay(feds_inst, nifc_inst, how='intersection')
        TP = OutputCalculation.truePos(feds_inst, nifc_inst)
        feds_area = OutputCalculation.areaCalculation(feds_inst)

        return TP / feds_area

    def recallCalculation(feds_inst, nifc_inst):
        """ TP/REF_B (nifc)
            TP == FRAP + FEDS agree on burned (intersect)
            REF_B == all burned of nifc/source
        """
        # overlay = gpd.overlay(feds_inst, nifc_inst, how='intersection')
        TP = OutputCalculation.truePos(feds_inst, nifc_inst)
        nifc_area = OutputCalculation.areaCalculation(nifc_inst)

        return TP / nifc_area

    def IOUCalculation(feds_inst, nifc_inst):
        """ IOU (inter over union)
            TP/(TP + FP + FN)
        """

        # overlay = gpd.overlay(feds_inst, nifc_inst, how='intersection')
        TP = OutputCalculation.truePos(feds_inst, nifc_inst)
        FP = OutputCalculation.falsePos(feds_inst, nifc_inst) # feds + nifc agree on no burning
        FN = OutputCalculation.falseNeg(feds_inst, nifc_inst) # feds thinks unburned when nifc burned

        return TP / (TP + FP + FN)

    def f1ScoreCalculation(feds_inst, nifc_inst):
        """ 2 * (Precision * Recall)/(Precision + Recall)
        """
        precision = OutputCalculation.precisionCalculation(feds_inst, nifc_inst)
        recall = OutputCalculation.recallCalculation(feds_inst, nifc_inst)
        calc = 2 * (precision*recall)/(precision+recall)

        return calc

    # @TODO: custom calc functions
    def symmDiffRatioCalculation(feds_inst, nifc_inst):
        """ symmetric difference calc, ratio 
            NOTE: error relative to NIFC/external soure
        """
        sym_diff = feds_inst.symmetric_difference(nifc_inst, align=False)
        # use item() to fetch int out of values
        assert sym_diff.shape[0] == 1, "Multiple sym_diff entries identified; pair accuracy evaluation will fail."
        # calculate error percent: (difference / "correct" shape aka nifc)
        symm_area = OutputCalculation.areaCalculation(sym_diff)
        nifc_area = OutputCalculation.areaCalculation(nifc_inst)
        # symmDiff_ratio = sym_diff.geometry.area.item() / nifc_inst.geometry.area.item()
        symmDiff_ratio = symm_area / nifc_area

        return symmDiff_ratio