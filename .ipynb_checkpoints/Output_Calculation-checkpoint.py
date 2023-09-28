""" 
Output_Calculation Class

"""

import glob
import logging
import pandas as pd
import geopandas as gpd
import fsspec
import boto3
import geopandas as gpd
import datetime as dt
import logging

from pyproj import CRS
from owslib.ogcapi.features import Features
from datetime import datetime, timedelta
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, EndpointConnectionError

# class imports
import Utilities
from Input_Reference import InputReference
from Input_VEDA import InputVEDA

class OutputCalculation():
    
    """ OutputCalculation
        Class representing output calculation of veda_input vs ref_input
    """
    
    # implemented output formats
    OUTPUT_FORMATS = ["txt", "json"]
    
    def __init__(self, 
                 veda_input: InputVEDA, 
                 ref_input: InputReference, 
                 output_format: str, 
                 output_maap_url: str,
                 day_search_range: int,
                 print_on: bool,
                 plot_on: bool):

        # USER INPUT / FILTERS
        self._veda_input = veda_input
        self._ref_input = ref_input
        self._output_format = output_format
        self._output_maap_url = output_maap_url
        self._day_search_range = day_search_range
        self._print_on = print_on
        self._plot_on = plot_on
        
        # PROGRAM SET
        self._polygons = None
        self._calculations = None # set from running the calculation -> dict of lists? index syncrhonized?
        self._dump = None # content to dump into file
        self._s3_url = None # possibly delete?
        
        # SINGLE SETUP
        self.__set_up_master()
        
    @property
    def veda_input(self):
        return self._veda_input
    
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
        assert self._day_search_range < 8, f"Excessive provided day range {self._day_search_range}; select smaller search period that is < 8 (or manually edit setting in __set_up_master of Output_Calculation.py"
        assert self._veda_input.crs == self._ref_input.crs, f"Mismatching CRS for VEDA and reference; must correct before continuing: veda: {self._veda_input.crs} vs ref: {self._ref_input.crs}"
        
        
        # run calculations
        self.__run_calculations() # --> internally finds best matches and runs on the best matches
        
        # TODO
        # self.__set_up_output_maap_file()
        # self.__write_to_output_file()
        
        # TODO
        if self._print_on:
            self.__print_output()
        if self._plot_on:
            self.__plot_output()
            
        return self
    
    def __set_up_valid_maap_url(self):
        """ given a maap-ops-workspace url, check if valid with naming + s3 access"""
        
        maap_ops_contained ="s3://maap-ops-workspace/shared/" in self._output_maap_url
        s3_url = self._output_maap_url 
        
        try:
            # try:
            s3 = boto3.client('s3')
            bucket, key, nested = Utilities.split_s3_path(s3_url)

            if nested:
                # iter and locate bucket
                # List objects in the parent bucket with the specified prefix
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
        # veda polygon index mapping to reference index of closest type (or None)
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
                                 
        for veda_ref_pair in index_pairs: # e.g. (4, 1) <- veda index 4 best matches with ref poly at index 1
                                 
            skip_first_key = True
                                 
            # no reference polygon --> attach none to tracked calculations
            if (veda_ref_pair[1] is None):
                for key in calculations:
                    if skip_first_key:
                        skip_first_key = False
                        continue  # Skip the first key
                    calculations[key].append(None)
                continue
           
            # fetch corresponding polygons
            veda_poly = self._veda_input.polygons[self._veda_input.polygons['index'] == veda_ref_pair[0]]
            ref_poly = self._ref_input.polygons[self._ref_input.polygons['index'] == veda_ref_pair[1]]
               
            # run through calculations
            ratio = OutputCalculation.ratioCalculation(veda_poly, ref_poly)
            accuracy = OutputCalculation.accuracyCalculation(veda_poly, ref_poly)
            precision = OutputCalculation.precisionCalculation(veda_poly, ref_poly)
            recall = OutputCalculation.recallCalculation(veda_poly, ref_poly)
            iou= OutputCalculation.IOUCalculation(veda_poly, ref_poly)
            f1 = OutputCalculation.f1ScoreCalculation(veda_poly, ref_poly) 
            symm_ratio = OutputCalculation.symmDiffRatioCalculation(veda_poly, ref_poly) # indep calc
            
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
            print(f'RESULTS FOR POLYGON VEDA AT INDEX {calculations["index_pairs"][i][0]} AGAINST REFERENCE POLYGON AT INDEX {calculations["index_pairs"][i][1]}:')
            print(f'Ratio: {vals[0]}, Accuracy: {vals[1]}, Precision: {vals[2]}, Recall: {vals[3]}, IOU: {vals[4]}, F1 {vals[5]}, Symmetric Ratio: {vals[6]}')
            print(f'All measurements in units {self._veda_input.polygons.crs.axis_info[0].unit_name}')
                                 
        return self
    
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
        
    
                                 
    # GENERAL PROCESSING METHODS
                                 
    def get_nearest_by_date(dataset, timestamp, dayrange: int):
        """ Identify rows of dataset with timestamp matches;
            expects year, month, date in datetime format
                dataset: input dataset to search for closest match
                timestamp: timestamp we want a close match for
            returns: dataset with d->m->y closest matches
        """

        # timestamp = timestamp.item()
        transformed = dataset.DATE_CUR_STAMP.tolist() # TODO: deal with this label? or make sure ref sets always have this
        clos_dict = {
          abs(timestamp.timestamp() - date.timestamp()) : date
          for date in transformed
        }

        res = clos_dict[min(clos_dict.keys())]

        # check on dayrange flexibility - trigger outer exception if failing
        if abs(timestamp.day - res.day) > dayrange and dayrange == 7:
            return None

        assert abs(timestamp.day - res.day) <= dayrange, "FATAL: No dates found in specified range; try a more flexible range by adjusting `dayrange` var"
        # fetch rows with res timestamp
        finalized = dataset[dataset['DATE_CUR_STAMP'] == res]

        return finalized
                                 
                                 
    def closest_date_match(self) -> list:
        """ given the veda and reference polygons -> return list mapping the veda input to closest reference polygons"""
        
        # store as (veda_poly index, ref_polygon index)
        matches = []

        # fetch polygons
        veda_polygons = self._veda_input.polygons
        ref_polygons = self._ref_input.polygons
        
        logging.info(f'Number of total veda_polygons: {len(self._veda_input.polygons.index)}')
        logging.info(f'Number of total ref_polygons: {len(self._ref_input.polygons.index)}')
        
        # iterate through all veda polys
        for veda_poly_i in range(veda_polygons.shape[0]):
            # grab veda polygon
            curr_veda_poly = veda_polygons.iloc[[veda_poly_i]]
            # indices of refs that intersected with this veda poly
            curr_finds = []
            
            # PHASE 1: FIND INTERSECTIONS OF ANY KIND
            for ref_poly_i in range(ref_polygons.shape[0]):
                curr_ref_poly = ref_polygons.iloc[[ref_poly_i]]
                intersect = gpd.overlay(curr_ref_poly, curr_veda_poly, how='intersection')
                if not intersect.empty:
                    curr_finds.append(ref_poly_i)
           
            if len(curr_finds) == 0:
                # for later calculations, this veda polygon is not paired with any ref poly
                logging.warning(f'NO MATCHES FOUND FOR VEDA_POLYGON AT INDEX: {veda_polygons["index"].iloc[veda_poly_i]}; UNABLE TO FIND BEST DATE MATCHES, ATTACHING NONE FOR REFERENCE INDEX')
               
                matches.append((veda_polygons['index'].iloc[veda_poly_i], None))
                continue
            
            
            timestamp = curr_veda_poly.t # veda time stamp - 2023-09-22T12:00:00 in str format 
            set_up_finds = ref_polygons.take(curr_finds)
                                 
            # PHASE 2: GET BEST TIME STAMP SET, TEST IF INTERSECTIONS FIT THIS BEST DATE
            try:
                timestamp = datetime.strptime(timestamp.values[0], "%Y-%m-%dT%H:%M:%S")
                time_matches = OutputCalculation.get_nearest_by_date(set_up_finds, timestamp, self._day_search_range)
            except Exception as e:
                logging.warning(f'Encountered error when running get_nearest_by_date: {e}')
                logging.warning(f'DUE TO ERR: VEDA POLY WITH INDEX {veda_polygons["index"].iloc[veda_poly_i]} HAS NO INTERSECTIONS AT BEST DATES:  ATTACHING NONE FOR REFERENCE INDEX')
                matches.append((veda_polygons['index'].iloc[veda_poly_i], None))
                continue
            if time_matches is None:
                logging.error(f'FAILED: No matching dates found even with provided day search range window: {self._day_search_range}, critical benchmarking failure.')
                sys.exit()
            
            # PHASE 3: FLATTEN TIME MATCHES + INTERSECTING
            # should multiple candidates occur, flag with error
            intersect_and_date = [time_matches.iloc[[indx]]['index'].values[0] for indx in range(time_matches.shape[0])]
            # intersect_and_date = [time_matches.iloc[[indx]] for indx in range(time_matches.shape[0])]
            assert len(intersect_and_date) != 0, "FATAL: len 0 should not occur with the intersect + best date array"
            if len(intersect_and_date) > 1:
                logging.warning(f'VEDA polygon at index {veda_polygons["index"].iloc[veda_poly_i]} has MULTIPLE qualifying polygons to compare against; will attach {len(intersect_and_date)} tuples for this index.')
            [matches.append((veda_polygons['index'].iloc[veda_poly_i], a_match)) for a_match in intersect_and_date]
            
                               
        logging.info('Nearest Date matching complete!')
        return matches
    
    def format_for_file(self):
        # TODO
        return 0
    
    def write_to_output_file(self):
        # TODO
        with fsspec.open(self._output_maap_url) as f:
            f.write(self._dump)

    
    #### WARNING: EXPERIMENTAL METHODS BELOW, NOT CONFORMING TO OOP DESIGN ###   
        
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
                             lowerPref):
        """ feds: feds source
            nifc: external source to compare to
            top_performance: best numeric value (default is worst value aka > 100 % error)
            top_tolerance: corresponding simplification with best performance
            base_tolerance: counter for tracking progress from limit -> 0
            calc_method
            lowerPref: true if a "better" score is considered a lower value

            return: top_tolerance (best tolerance value from recursion)

        """
        if base_tolerance == 0:
            return top_tolerance

        # simplify + calculate performance
        simplified_feds = simplify_geometry(feds, base_tolerance)
        curr_performance = calc_method(simplified_feds, nifc)

        # if performance "better" (depends on passed bool / method) -> persist
        if curr_performance < top_performance and lowerPref:
            top_performance = curr_performance
            top_tolerance = base_tolerance
        elif curr_performance > top_performance and not lowerPref:
            top_performance = curr_performance
            top_tolerance = base_toleranc

        # reduce and keep recursing down
        base_tolerance -= 1

        return best_simplification(feds, nifc, top_performance, top_tolerance, base_tolerance, calc_method, lowerPref)


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

        return 0

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