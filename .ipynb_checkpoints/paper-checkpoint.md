---
title: 'FEDS-PEC: A Python Module for Streamlining NASA Fire Perimeters Comparisons to Alternative Mapping Methods'
tags:
  - NASA
  - wildfire
  - fire perimeter
  - Python
authors:
  - name: Katrina Sharonin
    orcid: 0000-0000-0000-0000
    equal-contrib: true
    affiliation: 1
  - name: Tempest McCabe
    equal-contrib: false 
    affiliation: 1
affiliations:
 - name: NASA Goddard Space and Flight Center
   index: 1
date: 10 January 2024
bibliography: paper.bib

---

# Summary

The Fire Event Data Suite-Polygon Evaluation and Comparison (FEDS-PEC) is a specialized Python module tailored to accelerate numerical comparison of variable fire perimeters mapping methods. The module is catered to run on the NASA Multi-Algorithm and Analysis Platform (MAAP) and to compare NASA’s FEDS fire perimeter product against fire perimeters from key stakeholder agencies (e.g. NIFC, CALFIRE, and WFIGS) along with user-inputted datasets. Ultimately FEDS-PEC is aimed at generating long-term performance assessments and assisting NASA researchers in identifying areas of needed improvement in the FEDS algorithm. Although specialized for FEDS, users can freely adapt the library for custom perimeter versus perimeter comparisons, enabling wildfire research. FEDS-PEC’s core functionality enables seamless access to multiple APIs and datasets along with numerical analysis. This is accomplished by providing template notebooks with which users can compare different databases of fire perimeters from a common syntax. Inputs include datasets of choice, region/bounding box, start time, end time, day search range and filters. The library visits the requested datasets, applies the region and search times, and performs diverse calculations including ratio, accuracy, precision, recall, IOU, F1 score, and symmetric ratio difference. Finally, FEDS-PEC returns the polygon metadata and corresponding calculations. Users can interact with the output by plotting the identified polygons and analyzing calculated values.

Overall, FEDS-PEC optimizes evaluation processes, empowering researchers and analysts to efficiently assess perimeter geospatial data without reinventing evaluation solutions. Designed for compatibility with Jupyter Notebooks and offering flexible options, FEDS-PEC strives to bridge the gap between the wildfire research community and firefighting agencies by making the evaluation of fire-perimeter products easy, accessible, and frequent.


# Statement of need

Over the past two decades, wildfires in the Western U.S. have increased in severity, frequency, and size (@dennison_large_2014, @weber_spatiotemporal_2020). Paired with the expansion of the wildland-urban interface (@radeloff_rapid_2018, @hammer_wildlandurban_2007), estimated national wildfire damage costs on an annualized basis range from $63.5 billion to $285.0 billion (@thomas_costs_2017). In addition, between 1901-2011, 674 civilian wildfire fatalities occurred in North America (@manzello_wildfires_2020). California wildfires have claimed 150 lives over the past 5 years alone [CAL FIRE top 20] and over 30% of total U.S. wildland firefighter fatalities from 1910-2010 @manzello_wildfires_2020.

With the growing risk to property and livelihood in the U.S., precise and efficient methods of tracking active fire spread are critical for supporting near real-time firefighting response and wildfire management decision-making. Several map-making methods are practiced by firefighting agencies to track fire size and location. Primary methods include GPS-walking, GPS flight, and infrared image interpretation (@noauthor_national_nodate). The latter method, infrared imaging (IR), is one of the most widely demanded due to daily data delivery for routine briefings and synoptic coverage; between 2013 and 2017, yearly IR requests for the USDA Forest Service’s National Infrared Operations Program (NIROPS) increased from about 1.4k to just over 3.0k [USFS NIROPS Poster]. However, aerial infrared imaging methods involve several acquisition challenges, including cost, sensor operation restrictions, limited ability to meet coverage demand, and latency.
Among NASA’s existing projects and tools, the development of thermal remote-sensing via satellites stands as a major potential augmentation to wildfire operations and mapping. The Moderate Resolution Imaging Spectroradiometer (MODIS) aboard the Aqua and Terra satellites, and the Visible Infrared Imaging Radiometer Suite (VIIRS) aboard S-NPP and NOAA 20 (formally known as JPSS-1), represent the primary tools for NASA’s wildfire remote-sensing initiative.

Satellite observations are harnessed to generate finalized fire perimeter products. One leading perimeter algorithm is the FEDS Fire Perimeters led by Yang Chen (@chen_california_2022). This system employs automated processes to aggregate and analyze VIIRS instrument data every 12 hours, identifying active fire pixels and delineating fire perimeters. Using an alpha shape algorithm, it integrates these data points, allowing for a comprehensive and dynamic tracking of fire attributes and shapes over time, facilitating near real-time monitoring of fire progression and characteristics within a region.
The integration of satellite products can address several issues faced by standard IR missions: satellites are not manned and therefore do not pose a safety risk when deployed, satellites do not impede in Fire Traffic Area, there is a standard temporal resolution for every instrument, tools can provide real-time data, data processing, interpretation, and access can be handled by programs such as NASA FIRMS, there is a fixed cost associated with only creation and maintenance of the satellite tool, with nationwide to global coverage potential.

However, the integration of satellite observations has been limited due to the various issues cited by USFS, including resolution scale (i.e. 2 km for MODIS), false positives, limited swath width, analysis support, latency, post-processing of data, and temporal resolution (@kuo_usda_nodate). Overall, USFS deems satellites most appropriate for strategic intelligence rather than tactical incident awareness and assessment (IAA), where IAA focuses on detailed intelligence on “fast moving dynamic fires” and strategic focuses on a wider operating picture. Most importantly, a key goal of the USFS is to: “Continue to evaluate satellite detection and mapping capability” (@kuo_usda_nodate slide 16).

Despite various challenges, emerging research and products continue to improve and demonstrate the strength of satellite imagery for wildfire applications. To demonstrate the robustness of satellite perimeter products and support firefighting agencies, there is a need to numerically compare satellite products with current agency mapping methods. By directly overlaying sources, both researchers and firefighting agencies can objectively assess and visualize the performance of different fire-measurement techniques. Most researchers generate their own scripts to perform these calculations. FEDS-PEC is designed to reduce redundancy and provide researchers with a quick-start toolkit to compare fire perimeter datasets. By uplifting researcher efficiency, the scientific community can more effectively collaborate with firefighting/stakeholder agencies to identify strengths, weaknesses, and opportunities for improvement.

# Statement of the Field

As of January 2024, to the authors’ best knowledge no other open-source comparison library for fire perimeters  exists. Of note are many spatial tools and packages exist for calculating metrics of spatial matching. Package examples include PySAL (@rey_pysal_2007), Shapely (@gillies_shapely_2023), and Geopandas (@bossche_geopandasgeopandas_2024). General GIS tool examples include ArcGIS Pro and QGIS.

Importantly, FEDS-PEC  is not a general spatial calculation package. Instead, it focuses on automating three problems common to fire science: 1) Providing access to different datasets, 2) aligning datasets, or identifying which perimeters from different datasets are likely describing the same fire, even if the perimeters may be from different times, shapes, and resolutions, 3) calculating the spatial agreement between perimeters that represent the same fire. While motivated by fire-research, these three problems may emerge in other fields where events are described by polygons, such as storm-tracking, plume tracking, and landslides.

# FEDS-PEC Project

![Sample result plot comparing a FEDS archive perimeter to a NIFC Archive Reference perimeter from US_2018_TO_2021_ANALYSIS_RUN.ipynb](images/finalized_with_legend_FEDS.jpg)

## Overview

FEDS-PEC will compare vector perimeters from different sources, perform multiple calculation functions, and output numerical and visual results (Figure 1). 

FEDS-PEC requires user inputs of time interval, region, and dataset settings to generate 3 objects: ``InputFEDS``, ``InputReference``, and ``OutputCalculation``. 

``InputFEDS`` represents the FEDS perimeter input. ``InputReference`` represents the stakeholder dataset (e.g. NIFC archive polygon, CAL FIRE historic perimeter, etc). ``OutputCalculation`` is an object which stores the results of comparing ``InputFEDS`` and ``InputReference``. It will generate verbose outputs that users can subsequently use to plot information. 

## Supported API for FEDS Perimeters
- FEDS perimeters are sourced via a single VEDA API; documentation can be found at @signell_veda_2023. However, only specific collections of the API are supported. See below implemented collections: 
    - public.eis_fire_lf_perimeter_archive
        - Description: Perimeter of cumulative fire-area, from fires over 5 km^2 in the Western United States. Every fire perimeter from 2018-2021.
    - public.eis_fire_lf_perimeter_nrt	
        - Description: Perimeter of cumulative fire-area, from fires over 5 km^2. Every fire perimeter currently present near–real time.


## Supported APIs for Reference Fire Perimeters
- NIFC Open Data: InterAgencyFirePerimeterHistory All Years View
    - Description:
    - URL: https://data-nifc.opendata.arcgis.com/maps/interagencyfireperimeterhistory-all-years-view 
    - `` ref_title = “InterAgencyFirePerimeterHistory_All_Years_View” ``
    - Note: This dataset has been predownloaded into a MAAP directory. Should users have access to MAAP and interest in a stable static version of the dataset, use `` ref_title = “Downloaded_InterAgencyFirePerimeterHistory_All_Years_View” ``
    - Note: Users can download this dataset via the provided link; select “download” and the “ShapeFile” option. 
- NIFC Open Data: WFIGS Current Interagency Fire Perimeters
    - Description:
    - URL: https://data-nifc.opendata.arcgis.com/maps/wfigs-current-interagency-fire-perimeters 
    - `` ref_title = “WFIGS_current_interagency_fire_perimeters” ``
    - Note: Users can download this dataset via the provided link; select “download” and the “ShapeFile” option. 
- California Department of Forestry and Fire Protection: California Fire Perimeters (all)
    - Description:
    - URL: https://gis.data.ca.gov/datasets/CALFIRE-Forestry::california-fire-perimeters-all-1/explore 
    - `` ref_title = “california_fire_perimeters_all” ``
    - Note: Users can download this dataset via the provided link; select “download” and the “ShapeFile” option. 

FEDS-PEC does not currently support all publicly available APIs of fire perimeters. Fire perimeter data is collected and controlled by a huge range of stakeholders globally. FEDS-PEC instead provides a template for including future APIs as research needs emerge. API’s are a relatively rare source of fire perimeter data. Fire perimeter data can be made by governments using classified data [i.e. US National Guard FireGuard program], or be derived from“one-off” event-level measurements that do not warrant the support of an API, or be curated by organizations that cannot support an API. By offering users the option to upload custom datasets, FEDS-PEC captures common research use-cases.

## Key Features 

- Geo-Time Matcher: 
    - Using user inputs, Match-Maker will access data sources and iterate between a specified time interval and geographic region. For the interval and region, it will pull all FEDS instances. Then for each FEDS instance, it intersects with the reference dataset and inspects the difference in time. If there is an intersection and the two polygons are within day_search_range days of each other, it will declare a match and report the indices of the respective polygons. The indices are applied directly to the objects via `` InputFeds._polygons `` and `` InputReference._polygons ``
    - Algorithm will still output results of matches that fall outside of `` day_search_range ``, but will indicate with verbose logging.

- Calculation-Analyzer:
    - If a successful match pair is produced, the Match-Maker calls on a series of calculation functions (ratio, accuracy, precision, recall, IOU, F1, symmetric ratio difference) and prints out the resulting values. 

- Plotter:
    - The program automatically generates plots for all FEDS/Reference pairs. Plot titles indicate FEDS and Reference timestamps, along with axes with latitude/longitude information in the user specified coordinate reference system.

- Incident-Labeler:
    - If a successful match pair is produced, the Incident-Labeler will assign an incident name to the FEDS polygon using a valid incident name column. The following column names are recognized as valid incident label column titles: `` ‘INCIDENT’, ‘poly_IncidentName’, ‘FIRE_NAME’ ``. For example, the NIFC archive dataset uses the column title INCIDENT to denote a wildfire incident name. If no valid column is found, FEDS polygons will remain nameless.

- Function-Optimal Polygon Refinement:
    - The user provides a function that they want to maximize or minimize. The program will recursively apply the shapely.simplify(threshold) function until the threshold is equivalent to near 0. The recursion initiates on a user start threshold, and increments down by a user-defined step size. The program returns the best value produced along with the corresponding threshold value which reproduces the best value.
    - Calling procedure: with an OutputCalculation object (e.g. my_output), call with a calculation method (function to optimize), lower preference indicator (True if a lower value is considered top performance, false if higher value is considered top performance), and a base tolerance (the threshold value fed into the shapely simplify function). The function returns a list of of threshold values which optimized the simplification, each entry corresponds to a FEDS and Reference pair.

```
best_threshold_collection = my_output.init_best_simplify(
                       calc_method, 
                       lowerPref, 
                       base_tolerance
                      )

```

- Persistent Output
    - In addition to the interactive iPython notebook environment, the user provides and output path and file format. The program then saves the calculation dictionary result into the specified file format.
    - Supported file formats
        - CSV
    - Example in demo input section (see any file in the ``/demo`` directory):
    
```
name_for_output_file = "test_run"
output_format = "csv"
user_path = "/projects/my-public-bucket/VEDA-PEC/results"
output_maap_url = f"{user_path}/{name_for_output_file}.{output_format}"
…
my_output = OutputCalculation(
                feds_firenrt,
                nifc_search,
                output_format, 
                output_maap_url,
                day_search_range,
                print_on,
                plot_on
                )

```
- TIF Analysis
    - With the resulting ``OutputCalculation`` object, users can call the method ``tif_analysis`` which returns a calculated value by taking each pair of FEDS and Reference, masking the TIF with the symmetric difference of the FEDS polygon over the reference polygon.
    - This function accepts three arguments, two of which are mandatory: tif_path (path to TIF file as a string), req_calc ( a string from the following choices: ``"MEDIAN", “MEAN”, “UNIQUE”``), date_restrict (optional, an integer indicated how many days absolute difference between FEDS and Reference are permitted). 
    - Example call: 
```
get_median = my_output.tif_analysis("/projects/my-public-bucket/tif_files/slopeLF/LC20_SlpD_220.tif", "MEDIAN", 100)

```

## Directory and File Structure

As of version 1.0, the FEDS-PEC project consists of the single repository ``feds-benchmarking`` (URL: https://github.com/ksharonin/feds-benchmarking). The repository consists of the following directories and files on the main branch, FEDS-PEC-Protected:

- Files in Main Directory
    - ``README.md``: the key document describing installation and configuration instructions. Contains detailed information on inputs and outputs.
    - ``Input_FEDS.py``: python file implementing the InputFEDS object
    - ``Input_Reference.py``: python file implementing the InputReference object
    - ``Output_Calculation.py``: python file implementing the OutputCalculation object
    - ``Utilities.py``: python file with miscellaneous helper functions for the FEDS-PEC algorithm
    - ``Env-feds.yml``: YAML file specifying dependencies for the conda environment generated by the Run_dps.sh shell script
- Sub-Directories
    - ``/results``: directory intended to hold user outputs. Users can specify any output path, but for convenience this directory along with CSV output examples is included.
    - ``/demos``: directory containing example iPython notebooks that demonstrate various use cases of the FEDS-PEC project. Each notebook contains a summary outlining objectives and steps.
        - ``US_2018_TO_2021_ANALYSIS_RUN.ipynb``
            - FEDS Dataset: ``public.eis_fire_lf_perimeter_archive``
            - Reference Datset: ``InterAgencyFirePerimeterHistory_All_Years_View``
        - ``CALFIRE_ALL_PERIMS_DEMO.ipynb``
            - FEDS Dataset: ``public.eis_fire_lf_perimeter_archive``
            - Reference Datset: ``california_fire_perimeters_all``
        - ``CAMP_DEMO_FEDS_Outline.ipynb``
            - FEDS Dataset: ``public.eis_fire_lf_perimeter_archive``
            - Reference Datset: ``InterAgencyFirePerimeterHistory_All_Years_View``
        - ``KINCADE_DEMO_FEDS_Outline.ipynb``
            - FEDS Dataset: ``public.eis_fire_lf_perimeter_archive``
            - Reference Datset: ``InterAgencyFirePerimeterHistory_All_Years_View``
        - ``NRT_QUARRY_DEMO.ipynb``
            - FEDS Dataset: ``public.eis_fire_lf_perimeter_nrt``
            - Reference Datset: ``WFIGS_current_interagency_fire_perimeters``
        - ``NRT_US_DEMO.ipynb``
            - FEDS Dataset: ``public.eis_fire_lf_perimeter_nrt``
            - Reference Datset: ``WFIGS_current_interagency_fire_perimeters``
    - ``/data``: a local directory used for intermediate steps during the algorithm when downloading datasets from API requests
    - ``/blank``: directory containing a blank iPython notebook for users to interact with 
``BLANK_FEDS_Outline.ipynb``
    - ``/misc``: directory containing miscellaneous helper scripts and notebooks
        - ``csv_to_shp_helper.ipynb``: notebook demonstrating how to convert a CSV column into an shape file (SHP) for GIS applications.
        - ``run_dps.sh``: shell script for creating env-feds conda enviornment. Use with caution as script may instantiate env in github repo 

## Calculation Formulas

All calculation formulas can be viewed in `Output_Calculation.py` as python methods.

## Logic and Workflow

![FEDS-PEC Geo-Time Matcher Logic Diagram](images/FEDS_PEC_Logic.drawio (2).png){ height=2600px }

## User Set-up Guide

The FEDS-PEC README.md provides detailed instructions for users.

## Reporting Issues and Submitting Feedback

For any bug and issues, users are encouraged to open a github issue on the official FEDS-PEC github. URL: https://github.com/ksharonin/feds-benchmarking/issues 

# Research Applications: Tentative Results with 2018-2021 United States FEDS VS. NIFC Archive

To demonstrate the potential research application of FEDS-PEC, the notebook ``US_2018_TO_2021_ANALYSIS_RUN.ipynb`` was run to produce CSV output files, each of which was consolidated into the result Table 1.
This notebook compares FEDS large fire archives API dataset [Link/number to citation] against the NIFC InterAgencyFirePerimeterHistory All Years View dataset [Link/number to citation] from January 2018 to December 2021 inclusive. The notebook was run on multiple time intervals which compose the 2018 to 2021 range due to the FEDS API limited to 9000 outputs per run. The notebook performs the standard FEDS-PEC procedure: for each FEDS-PEC match via temporal and geographical matching, a pair is formed. For every pair, FEDS-PEC calculations the ratio, accuracy, precision, recall, IOU, F1, and Symmetric Ratio.

[TODO- finish analysis, insert table, insert citation]

# Acknowledgements

[TODO]
EIS-FIRE, NASA GSFC Pathways program

# References