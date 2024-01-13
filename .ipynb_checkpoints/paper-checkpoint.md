---
title: 'FEDS-PEC: A Python Module for Streamlining NASA Fire Perimeters Comparisons to Alternative Mapping Methods'
tags:
  - NASA
  - Wildfire
  - Fire perimeter
  - Python
authors:
  - name: Katrina Sharonin
    orcid: 0009-0000-5146-2633
    equal-contrib: false
    affiliation: 1
  - name: Tempest McCabe
    orcid: 0000-0002-8901-3267
    equal-contrib: false 
    affiliation: 1
  - name: Yang Chen
    orcid: 0000-0002-0993-7081
    equal-contrib: false 
    affiliation: 2
affiliations:
 - name: NASA Goddard Space and Flight Center
   index: 1
 - name: University of California, Irvine
   index: 2
date: 10 January 2024
bibliography: paper.bib

---

# Summary

The Fire Event Data Suite-Polygon Evaluation and Comparison (FEDS-PEC) is a specialized Python module tailored to accelerate numerical comparison of fire perimeter products derived from different mapping methods. Currently, the module is catered to compare NASA’s FEDS fire perimeter product, generated from an algorithm that uses satellite observations, against fire perimeters from key stakeholder agencies (e.g. NIFC, CALFIRE, and WFIGS) along with user-inputted datasets. Ultimately FEDS-PEC is aimed at generating long-term performance assessments and assisting NASA researchers in identifying areas of needed improvement in the FEDS algorithm. Although specialized for FEDS, users can freely adapt the library for custom perimeter versus perimeter comparisons, enabling wildfire research. FEDS-PEC’s core functionality enables seamless access to multiple APIs and datasets along with numerical analysis. This is accomplished by providing template notebooks with which users can compare different databases of fire perimeters from a common syntax. Inputs include datasets of choice, region/bounding box, start time, end time, day search range and filters. The library visits the requested datasets, applies the region and search times, and performs diverse calculations including ratio, accuracy, precision, recall, IOU, F1 score, and symmetric ratio difference. Finally, FEDS-PEC returns the polygon metadata and corresponding calculations. Users can interact with the output by plotting the identified polygons and analyzing calculated values.

Overall, FEDS-PEC optimizes evaluation processes, empowering researchers and analysts to efficiently assess perimeter geospatial data without reinventing evaluation solutions. Designed for compatibility with Jupyter Notebooks and offering flexible options, FEDS-PEC strives to bridge the gap between the wildfire research community and firefighting agencies by making the evaluation of fire-perimeter products easy, accessible, and frequent.


# Statement of need

Over the past two decades, wildfires in the Western U.S. have increased in severity, frequency, and size (@dennison_large_2014, @weber_spatiotemporal_2020). Paired with the expansion of the wildland-urban interface (@radeloff_rapid_2018, @hammer_wildlandurban_2007), estimated national wildfire damage costs on an annualized basis range from $63.5 billion to $285.0 billion (@thomas_costs_2017). In addition, between 1901-2011, 674 civilian wildfire fatalities occurred in North America (@manzello_wildfires_2020). In 2020 alone, California wildfires claimed 45 lives (@porter_2020_2020).

With the growing risk to property and livelihood in the U.S., precise and efficient methods of tracking active fire spread are critical for supporting near real-time firefighting response and wildfire management decision-making. Several map-making methods are practiced by firefighting agencies to track fire size and location. Primary methods include GPS-walking, GPS flight, and infrared image interpretation (@noauthor_nwcg_2014). The latter method, infrared imaging (IR), is one of the most widely demanded due to daily data delivery for routine briefings and synoptic coverage; between 2013 and 2017, yearly IR requests for the USDA Forest Service’s National Infrared Operations Program (NIROPS) increased from about 1.4k to just over 3.0k (Figure 1, @mellin_2021_nodate). However, aerial infrared imaging methods involve several acquisition challenges, including cost, sensor operation restrictions, limited ability to meet coverage demand, and latency.

![2006-2021 NIROPS Aircraft Infrared Imaging Resources Requests by Year, figure sourced from @mellin_2021_nodate](images/NIROP_requests_USFS.jpg)

Among NASA’s existing projects and tools, the development of thermal remote-sensing via satellites stands as a major potential augmentation to wildfire operations and mapping. The Moderate Resolution Imaging Spectroradiometer (MODIS) aboard the Aqua and Terra satellites, Geostationary Operational and Environmental Satellites (GOES), and the Visible Infrared Imaging Radiometer Suite (VIIRS) aboard S-NPP and NOAA 20 (formally known as JPSS-1), represent fundamental tools for NASA’s wildfire remote-sensing capabilities.

Satellite observations are harnessed to generate fire perimeter products. One leading perimeter algorithm is the FEDS Fire Perimeters led by Yang Chen (@chen_california_2022). This system employs automated processes to aggregate and analyze VIIRS instrument data every 12 hours, identifying active fire pixels and delineating fire perimeters. Using an alpha shape algorithm, it integrates these data points, allowing for a comprehensive and dynamic tracking of fire attributes and shapes over time, facilitating near real-time monitoring of fire progression and characteristics within a region.
The integration of satellite products can address several issues faced by aircraft IR missions: satellites are not manned and therefore do not pose a safety risk when deployed, satellites do not impede in Fire Traffic Area, there is a standard temporal resolution for every instrument, tools can provide real-time data, data processing, interpretation, and access can be handled by programs such as NASA FIRMS, there is a fixed cost associated with only creation and maintenance of the satellite tool, with nationwide to global coverage potential.

However, the integration of satellite observations has been limited due to the various issues cited by United State Forest Service (USFS), including resolution scale (i.e. 2 km for MODIS), false positives, limited swath width, analysis support, latency, post-processing of data, and temporal resolution (@olivia_proceedings_nodate, @usda_forest_service_fire_2020). Overall, USFS deems satellites most appropriate for strategic intelligence rather than tactical incident awareness and assessment (IAA), where IAA focuses on detailed intelligence on “fast moving dynamic fires” and strategic focuses on a wider operating picture. Most importantly, a key goal of the USFS is to: “Continue to evaluate satellite detection and mapping capability” (@usda_forest_service_fire_2020).

Despite various challenges, emerging research and products continue to improve and demonstrate the strength of satellite imagery for wildfire applications. To demonstrate the robustness of satellite perimeter products and support firefighting agencies, there is a need to numerically compare satellite products with current agency mapping methods. By directly overlaying sources, both researchers and firefighting agencies can objectively assess and visualize the performance of different fire-measurement techniques. Most researchers generate their own scripts to perform these calculations. FEDS-PEC is designed to reduce redundancy and provide researchers with a quick-start toolkit to compare fire perimeter datasets. By uplifting researcher efficiency, the scientific community can more effectively collaborate with firefighting/stakeholder agencies to identify strengths, weaknesses, and opportunities for improvement.

# Statement of the Field

As of January 2024, to the authors’ best knowledge no other open-source comparison library for fire perimeters  exists. Of note are many spatial tools and packages exist for calculating metrics of spatial matching. Package examples include PySAL (@rey_pysal_2007), Shapely (@gillies_shapely_2023), and Geopandas (@bossche_geopandasgeopandas_2024). General GIS tool examples include ArcGIS Pro and QGIS.

Importantly, FEDS-PEC  is not a general spatial calculation package. Instead, it focuses on automating three problems common to fire science: 1) Providing access to different datasets, 2) aligning datasets, or identifying which perimeters from different datasets are likely describing the same fire, even if the perimeters may be from different times, shapes, and resolutions, 3) calculating the spatial agreement between perimeters that represent the same fire. While motivated by fire-research, these three problems may emerge in other fields where events are described by polygons, such as storm-tracking, plume tracking, and landslides.

# FEDS-PEC Project

![Sample result plot comparing a FEDS archive perimeter to a NIFC Archive Reference. Perimeter generated via the plot module. See US_2018_TO_2021_ANALYSIS_RUN.ipynb in demo directory for above figure.](images/finalized_with_legend_FEDS.jpg)

## Overview

FEDS-PEC will compare vector perimeters from different sources, perform multiple calculation functions, and output numerical and visual results (Figure 2). 

FEDS-PEC requires user inputs of time interval, region, and dataset settings to generate 3 objects: ``InputFEDS``, ``InputReference``, and ``OutputCalculation``. 

``InputFEDS`` represents the FEDS perimeter input. ``InputReference`` represents the stakeholder dataset (e.g. NIFC archive polygon, CAL FIRE historic perimeter, etc). ``OutputCalculation`` is an object which stores the results of comparing ``InputFEDS`` and ``InputReference``. It will generate verbose outputs that users can subsequently use to plot information. 

## Supported API for FEDS Perimeters
- FEDS perimeters are sourced via a single VEDA API; documentation can be found at @signell_veda_2023. However, only specific collections of the API are supported. See below implemented collections: 
    - public.eis_fire_lf_perimeter_archive
        - Description: Perimeter of cumulative fire-area, from fires over 5 km^2 in the Western United States. Every fire perimeter from 2018-2021.
    - public.eis_fire_lf_perimeter_nrt	
        - Description: Perimeter of cumulative fire-area, from fires over 5 km^2 in the Contiguous United  States of the current year. 


## Supported APIs for Reference Fire Perimeters
- NIFC Open Data: InterAgencyFirePerimeterHistory All Years View
    - Description: The layer encompasses the final fire perimeter datasets of the USDA Forest Service, US Department of Interior Bureau of Land Management, Bureau of Indian Affairs, Fish and Wildlife Service, and National Park Service, the Alaska Interagency Fire Center, CalFire, and WFIGS History. Requirements for fire perimeter inclusion, such as minimum acreage requirements, are set by the contributing agencies. Geospatial coverage: United States. Time period covered: 1909 - 2021.
    - URL: [https://data-nifc.opendata.arcgis.com/maps/interagencyfireperimeterhistory-all-years-view](https://data-nifc.opendata.arcgis.com/maps/interagencyfireperimeterhistory-all-years-view)
    - `` ref_title = “InterAgencyFirePerimeterHistory_All_Years_View” ``
    - Note: This dataset has been predownloaded into a MAAP directory. Should users have access to MAAP and interest in a stable static version of the dataset, use `` ref_title = “Downloaded_InterAgencyFirePerimeterHistory_All_Years_View” ``
    - Note: Users can download this dataset via the provided link; select “download” and the “ShapeFile” option. 
- NIFC Open Data: WFIGS Current Interagency Fire Perimeters
    - Description: Best available perimeters for recent and ongoing wildland fires in the United States hosted by The Wildland Fire Interagency Geospatial Services (WFIGS) Group which provides authoritative geospatial data products under the interagency Wildland Fire Data Program. Perimeters are not available for every incident. Geospatial coverage: United States. Time period covered depends on fire size: Records are removed from this service under the following conditions:
        - If the fire size is less than 10 acres (Size Class A or B) and fire information has not been updated in more than 3 days. 
        - If the fire size is between 10 and 100 acres (Size Class C) and fire information hasn't been updated in more than 8 days. 
        - If the fire size is larger than 100 acres (Size Class D-L) but fire information hasn't been updated in more than 14 days.
    - URL: [https://data-nifc.opendata.arcgis.com/maps/wfigs-current-interagency-fire-perimeters](https://data-nifc.opendata.arcgis.com/maps/wfigs-current-interagency-fire-perimeters)
    - `` ref_title = “WFIGS_current_interagency_fire_perimeters” ``
    - Note: Users can download this dataset via the provided link; select “download” and the “ShapeFile” option. 
- California Department of Forestry and Fire Protection: California Fire Perimeters (all)
    - Description: CAL FIRE Wildfire Perimeters and Prescribed Burns. The service includes layers that are data subsets symbolized by size and year. Geospatial coverage: California. Time period covered: 1878 - Present.
    - URL: [https://gis.data.ca.gov/datasets/CALFIRE-Forestry::california-fire-perimeters-all-1/explore](https://gis.data.ca.gov/datasets/CALFIRE-Forestry::california-fire-perimeters-all-1/explore)
    - `` ref_title = “california_fire_perimeters_all” ``
    - Note: Users can download this dataset via the provided link; select “download” and the “ShapeFile” option. 

FEDS-PEC does not currently support all publicly available APIs of fire perimeters. Fire perimeter data is collected and controlled by a large range of stakeholders globally. FEDS-PEC instead provides a template for including future APIs as research needs emerge. API’s are a relatively rare source of fire perimeter data. Fire perimeter data can be made by governments using classified data [i.e. US National Guard FireGuard program], or be derived from“one-off” event-level measurements that do not warrant the support of an API, or be curated by organizations that cannot support an API. By offering users the option to upload custom datasets, FEDS-PEC captures common research use-cases.

## Key Features 

- Geo-Time Matching: 
    - Using user inputs, Match-Maker will access data sources and iterate between a specified time interval and geographic region. For the interval and region, it will pull all FEDS instances. Then for each FEDS instance, it intersects with the reference dataset and inspects the difference in time. If there is an intersection and the two polygons are within day_search_range days of each other, it will declare a match and report the indices of the respective polygons. The indices are applied directly to the objects via `` InputFeds._polygons `` and `` InputReference._polygons ``
    - Algorithm will still output results of matches that fall outside of `` day_search_range ``, but will indicate with verbose logging.

- Calculation-Analyzing:
    - If a successful match pair is produced, the Match-Maker calls on a series of calculation functions (ratio, accuracy, precision, recall, IOU, F1, symmetric ratio difference) and prints out the resulting values. 

- Plotting:
    - The program automatically generates plots for all FEDS/Reference pairs. Plot titles indicate FEDS and Reference timestamps, along with axes with latitude/longitude information in the user specified coordinate reference system.

- Incident-Labeling:
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


- Data Output
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

As of version 1.0.0, the FEDS-PEC project consists of the single repository ``feds-benchmarking`` (URL: [https://github.com/ksharonin/feds-benchmarking] (https://github.com/ksharonin/feds-benchmarking)). The repository consists of the following directories and files on the main branch, FEDS-PEC-Protected:

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

![FEDS-PEC Geo-Time Matcher Logic Diagram](images/FEDS_PEC_Logic.drawio (2).png){ height=2500px }

## User Set-up Guide

The FEDS-PEC README.md provides detailed instructions for users.

## Reporting Issues and Submitting Feedback

For any bug and issues, users are encouraged to open a github issue on the official FEDS-PEC github. URL: [https://github.com/ksharonin/feds-benchmarking/issues](https://github.com/ksharonin/feds-benchmarking/issues)

# Research Applications: 2018-2021 United States FEDS Perimeter Archive VS. NIFC InterAgencyFirePerimeterHistory All Years View

To demonstrate the potential research application of FEDS-PEC, the notebook ``US_2018_TO_2021_ANALYSIS_RUN.ipynb`` was run to produce CSV output files, each of which was consolidated into the result Table 1.
This notebook compares FEDS large fire archives API dataset [Link/number to citation] against the NIFC InterAgencyFirePerimeterHistory All Years View dataset (@signell_veda_2023) from January 2018 to December 2021 inclusive. The notebook was run on multiple time intervals which compose the 2018 to 2021 range due to the FEDS API limited to 9000 outputs per run. The notebook performs the standard FEDS-PEC procedure: for each FEDS-PEC match via temporal and geographical matching, a pair is formed. For every pair, FEDS-PEC calculates the ratio, accuracy, precision, recall, IOU, F1, and Symmetric Ratio.

| Absolute Day Difference | Number of FEDS/Reference Pairs | Median Ratio | Median Accuracy | Median Precision | Median Recall | Median IOU | Median F1 | Median Symmetric Ratio (FEDS - Reference) |
|-------------------------|--------------------------------|--------------|------------------|-------------------|--------------|------------|-----------|--------------------------------------------|
|           0             |               4                |    0.876     |      0.821       |       0.766       |     0.671     |    0.23    |   0.445   |                0.737                       |
|           1             |               15               |    1.046     |      0.673       |       0.798       |     0.646     |   0.347    |   0.571   |                0.889                       |
|           2             |               8                |    0.966     |      0.834       |       0.713       |     0.626     |   0.312    |   0.653   |                0.602                       |
|           3             |               9                |    0.615     |      0.591       |       0.862       |     0.485     |   0.304    |   0.619   |                0.597                       |
|           4             |               10               |    0.967     |      1.057       |       0.787       |     0.766     |   0.431    |   0.779   |                0.435                       |
|           5             |               6                |    0.88      |      0.737       |       0.677       |     0.6       |   0.191    |   0.509   |                0.807                       |
|           6             |               8                |    1.216     |      0.794       |       0.763       |     0.867     |   0.329    |   0.631   |                0.552                       |
|           7             |               7                |    0.579     |      0.576       |       0.804       |     0.485     |   0.09     |   0.181   |                0.924                       |
|           8+            |               132              |    0.974     |      0.703       |       0.774       |     0.612     |   0.115    |   0.236   |                0.944                       |
[]{label="Table 1: 2018-2021 United States FEDS Perimeter Archive VS. NIFC InterAgencyFirePerimeterHistory All Years View Statistical Results, rounded to the third decimal place"}

## Discussion

An example output table for the ``US_2018_TO_2021_ANALYSIS_RUN.ipynb`` run is demonstrated in Table 1. Each CSV row entry represents an absolute day difference category (how far apart in days the FEDS and Reference timestamp are). FEDS-Reference pairs occurring 1 day appart are sorted into the 1 day category, 2 day into 2 day, etc. In addition, the number of pairs per category is displayed in the “Numer of FEDS/Reference Pairs” column. Lastly, for each day difference category, there are 7 calculation type columns (ratio, accuracy precision, recall, IOU, F1, symmetric ratio). Each calculation typecolumn value is the median of all calculations of the specified type, per entries in the category (e.g. 0.876 is the median value of all ratio values of FEDS/Reference pairs in the 0 day difference category).  

One potential interpretation of the results in Table 1 is after 4 days of difference, overall accuracy begins to decrease. However, 8+ day difference row stands as an exception, likely indicating that there are wildfire perimeters slowing in growth, such that satellite observations recreate the growth despite the absolute day difference.  

However, it is important to note that the timestamps of the NIFC InterAgencyFirePerimeterHistory All Years View dataset may vary in accuracy (e.g. timestamp records last edit of polygon, not actual polygon creation). This challenge is one of many that can be faced when using third party datasets for fire perimeter research, which can be overcome by manual inspection of data and plotting datasets, all supported by FEDS-PEC outputs.

Overall, this type of summary would be useful for more thoroughly examining the perimeter accuracy and growth relationship with time in the future. 


# Author contribution section:

Katrina Sharonin conceived of the project, designed and wrote software. Katrina Sharonin also wrote the JOSS paper and documentation. Tempest McCabe tested software and advised on project direction. 

# Acknowledgements

Support for this project was provided by NASA's Earth Information System (EIS) Project, and the NASA Goddard Space Flight Center Pathways Program. 

# References