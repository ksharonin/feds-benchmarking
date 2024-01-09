# FEDS-PEC (Polygon Evaluation and Comparison) Module Documentation

## Authors

Authors: Katrina Sharonin (KS)

Co-Authors: Tempest McCabe (TM)

KS conceived of the project, designed and wrote software. KS wrote paper and documentation. TM tested software and advised on project direction. 

## Introduction

Welcome to the Fire Event Data Suite - Polygon Evaluation and Comparison (FEDS-PEC) module. FEDS-PEC is a Python library designed to facilitate benchmarking and evaluation of geospatial data, specifically tailored for [FEDS fire perimeters](https://nasa-impact.github.io/veda-docs/example-notebooks/wfs.html). This module allows users to compare these fire perimeters with reference datasets and perform various calculations, including ratio, accuracy, precision, recall, IOU (Intersection over Union), F1 score, and symmetric ratio. The primary goal of FEDS-PEC is to streamline the process of conducting such evaluations, saving time for researchers and analysts. This README provides detailed information on how to install, use, and contribute to the FEDS-PEC module.

## Statement of Need

### What is FEDS-PEC?

FEDS-PEC is a specialized Python module designed for geospatial data analysis, specifically tailored for FEDS fire perimeters. It offers the following key features:

- Interaction through Jupyter Notebooks (e.g. `KINCADE_DEMO_FEDS_Outline.ipynb`, `BLANK_PEC_Outline.ipynb`).
- The flexibility to use predefined reference datasets or user-uploaded/defined datasets.
- A wide range of calculations, including ratio, accuracy, precision, recall, IOU, F1 score, and symmetric ratio.
- Dedicated support for fire perimeter data, with plans to expand support for additional datasets based on community feedback.
- Convenient output formats for research and archival purposes.

### Why Use FEDS-PEC?

FEDS-PEC eliminates the need for users to recreate/repeat solutions when comparing and evaluating perimeter datasets. By leveraging this module, researchers and analysts can quickly and efficiently compare the FEDS fireperimeter dataset against a reference data set of their choosing. Users can focus their efforts on dataset selection and analysis, rather than spending time implementing and testing software for comparisons and calculations.

### Who Can Benefit from FEDS-PEC?

FEDS-PEC is primarily aimed at users of the NASA FEDS algorithm perimeters and the broader Earth science research community.

## Installation Instructions

Steps to install and use FEDS-PEC:

1. **Conda Environment Setup:** Run the `run-dps.sh` shell script to create the `env-feds` Conda environment. (NOTE: do not instantiate your conda enviornment in a git repository it causes high memory usage) 

2. **Notebook Setup:** Edit or make a copy of the `BLANK_FEDS_Outline.ipynb` located in the `blank` directory.

3. **Kernel Selection:** Ensure that the selected Jupyter Notebook kernel is the `env-feds` environment.

4. **Quickstart:** Follow the instructions in the notebook, specifically the "User Inputs for Comparison" section, to get started.

## Input Settings
This section describes inputs for FEDS and reference datasets and acceptable values. Some input options may be implemented or unimplemented due to development

### FEDS Input Settings
- `title`: select predefined title sourced from the api, or choose `none` if using a custom local input
    - Implemented:
        - `"firenrt"`: VEDA api fire perimeter dataset
            - Documentation: https://nasa-impact.github.io/veda-docs/notebooks/tutorials/mapping-fires.html
            - VEDA Dashboard View: https://www.earthdata.nasa.gov/dashboard/data-catalog/fire

- `collection`: if using a predefined api dataset, choose a corresponding collection, otherwise choose `none` if using a custom local input
    - Implemented:
        - Corresponding title: `"firenrt"`
            - `"public.eis_fire_lf_perimeter_archive"`: Perimeter of cumulative fire-area, from fires over 5 km^2 in the Western United States. Every fire perimeter from 2018-2021.
            - `'public.eis_fire_lf_perimeter_nrt'`: Perimeter of cumulative fire-area, from fires over 5 km^2. Every fire perimeter from current year to date.
    - Not implemented:
        - Corresponding title: `"firenrt"`
            - `"public.eis_fire_lf_fireline_archive"`: collection of historic firelines which are line geometry representing historic active fire fronts
            - `"public.eis_fire_snapshot_fireline_nrt"`: Active fire line as estimated by new VIIRS detections. Most fire line from the last 20 days.
                - Disclaimer: holds perimeters and may repeat calculations
            - `"public.eis_fire_snapshot_perimeter_nrt"`: Perimeter of cumulative fire-area. Most recent perimeter from the last 20 days
            - `'public.eis_fire_lf_nfplist_nrt'`,
            - `'public.eis_fire_lf_nfplist_archive'`,
            - `'public.eis_fire_lf_newfirepix_archive'`: New pixel detections that inform a given time-step’s perimeter and fireline calculation. Availible for Western United States from 2018-2021.
            - `'public.eis_fire_snapshot_newfirepix_nrt'`: New pixel detections that inform a given time-step’s perimeter and fireline calculation. Availible from start of current year to date.
            - `'public.eis_fire_lf_fireline_nrt'`: Active fire line as estimated by new VIIRS detections, from fires over 5 km^2. Every fire line from current year to date.
- `access_type`:
    - Implemented: 
        - `api`: the VEDA API is an open-source collection of datasets which includes the FEDS fire perimeter dataset. Select this option for the following titles:
            - `"firenrt"`
            - For more information, see documentation: https://nasa-impact.github.io/veda-docs/
- `limit`: amount of features to consider for FEDS API access; warning appears if it misses any entries. Recommended value is 9000, the API limit maximum.
- `filter`: `False` or a valid query that compiles with data set e.g. `"farea>5 AND duration>2"`; invalid queries will result in error
- `apply_final_fire`: for `"firenrt`"  set this to `True` if you want the only the latest fireID to be taken per unique FireID, set `False` for other datasets 

### Reference Input Settings

- `title`:
    - Implemented:
        - `"InterAgencyFirePerimeterHistory_All_Years_View`: a **dynamic** shp datset containing all fire perimeters up to 2023 documented by the National Interagency Fire Center (NIFC) for the United States
            - Agency: National Interagency Fire Center (NIFC)
            - Source: https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/InterAgencyFirePerimeterHistory_All_Years_View/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson
            - Update frequency: every 5 minutes
            - Time period covered: 1909 - Present
            - Geospatial coverage: United States
        - `"Downloaded_InterAgencyFirePerimeterHistory_All_Years_View`: a **static** shp datset containing all fire perimeters up to 2023 documented by the National Interagency Fire Center (NIFC) for the United States. Provided as a backup for users unable to access ArcGIS services at time of running FEDS-PEC.
            - Agency: National Interagency Fire Center (NIFC)
            - Source: https://data-nifc.opendata.arcgis.com/datasets/nifc::interagencyfireperimeterhistory-all-years-view/explore?location=32.468087%2C-122.087025%2C3.89 
            - Update frequency: one time/static, downloaded to maap directory once by author
            - Time period covered: 1909 - 2023
            - Geospatial coverage: United States
        - `"WFIGS_current_interagency_fire_perimeters"`: a dynamic shp dataset containing current wildfire perimeters documented by  by the National Interagency Fire Center (NIFC) for the United States; program activately queries the ArcGIS online source
            - Agency: National Interagency Fire Center (NIFC)
            - Source: https://data-nifc.opendata.arcgis.com/datasets/nifc::wfigs-current-interagency-fire-perimeters/explore?location=0.000000%2C0.000000%2C2.48 
            - Update frequency: every 5 minutes
            - Time period covered: Present
            - Geospatial coverage: United States
        - `"california_fire_perimeters_all"`: a dynamic shp dataset containing all California fire perimeters up to current date and maintained by CAL FIRE. Program activately queries the ArcGIS online source
            - Agency: California Department of Forestry and Protection (CAL FIRE)
            - Source: https://hub-calfire-forestry.hub.arcgis.com/datasets/CALFIRE-Forestry::california-fire-perimeters-all-1/explore?location=37.471701%2C-119.269132%2C6.65
            - Update frequency: 
            - Time period covered: 1878-Present
            - Geospatial coverage: California
- `control_type`:
    - Implemented:
        - `"defined"`: flag used for when any of the above defined datasets is applied
        - `"custom"`: flag used for when a user supplies a custom dataset 
- (OPTIONAL, UNLESS USING CUSTOM) `custom_url`
    - Implemented:
        - `"none"`: default, when defined datasets are applied
        - `"(user custom url here)"`: user enters the path to their dataset
- (OPTIONAL, UNLESS USING CUSTOM) `custom_read_type`
    - Implemented:
        - `"none"`: default, when defined datasets are applied
        - `"local"`: user indicates the file is local on their machine
- (OPTIONAL, UNLESS USING CUSTOM) `custom_col_assign`: empty dicionary `{}` or a dictionary containing the following keys: `time`, `time_format`, and (OPTIONAL) `incident_name`. The dictionary maps the necessary arguments for the FEDS-PEC program on custom datasets. Information on provided values:
    - `time`: type `str`, name of the column of the custom dataset corresponding to the timestamp
    - `time_format`: type `str`, a format code string for the `datetime.strptime()` method. e.g. `"%Y%M%d"`. Python documentation for format coding: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior 
    - `incident_name`: type `str`, if applicable, the name of the column containing incident titles for each shape. 
- (OPTIONAL) `filter`: `False` or a valid query that compiles with data set e.g. `"farea>5 AND duration>2"`; invalid queries will result in error, user discretion advised.

### Shared Input Settings
Inputs shared between FEDS and Reference
- `search_start`/ `search_stop`
    - Date search range for the FEDS/Reference Datasets. FEDS-PEC notebooks only requires integers and will apply a formatting procedure via helper functions. 
    - Formatting procedure:
    ``` 
    
    # START TIME
    year_start = 2020
    month_start = 7 
    day_start = 1
    hour_start = 0
    minute_start = 0
    second_start = 0
    tz_offset_hours_start = 0
    tz_offset_minutes_start = 0
    utc_offset_start = '00:00'

    # END TIME
    year_stop = 2020
    month_stop = 8
    day_stop = 30
    hour_stop = 0
    minute_stop = 0
    second_stop = 0
    tz_offset_hours_stop = 0
    tz_offset_minutes_stop = 0
    utc_offset_stop = '00:00'
    
    # stop date formatting
    search_start = Utilities.format_datetime(year_start, 
                                         month_start, 
                                         day_start, 
                                         hour_start, 
                                         minute_start, 
                                         second_start, 
                                         tz_offset_hours_start, 
                                         tz_offset_minutes_start,
                                         utc_offset_start)
    # stop date formatting
    search_stop = Utilities.format_datetime(year_stop, 
                                            month_stop, 
                                            day_stop, 
                                            hour_stop, 
                                            minute_stop, 
                                            second_stop, 
                                            tz_offset_hours_stop, 
                                            tz_offset_minutes_stop,
                                            utc_offset_stop)


    ```
- `crs`
    - Type `str`, coordinate reference system of the program, entered as a str of the number e.g. ``"3857"` representing EPSG:3857
- `search bbox`: 
    - Geographic bounding box for the FEDS dataset query, formatted as: [top left longitude, top left latitude, bottom right longitude, bottom righ latitude] e.g. US bounding box = `["-125.0", "24.396308", "-66.93457", "49.384358"]`
- `day_search_range`: 
    - Integer x such that 0 <= x, used to search for matching reference polygons e.g. if x = 5 FEDS polygon finds an intersecting polygon, but it is 6 days difference in timestamp, it will not be included in the resulting output pairs.

### Output Settings
To assist users in persisting output calculations and viewing plots, FEDS-PEC provides the following output settings:
- `print_on`: 
    - Type `bool`, `True` will print out identified FEDS and Reference matches along with calculations should the match be within a valid time range and intersect. `False` will suppress the print.
- `plot_on`: 
    - Type `bool`, `True` will output plots of identified FEDS and Reference matches that intersect and are in a valid time range, with default plot coloring is **FEDS == red** and **Reference == gold with hatching**. `False` will suppress plots.
- `name_for_output_file`:  
    - Name of output file without file extension, e.g. "test_run"
- `output_format`:
    - Output file format for results
    - Implemented:
        - `"csv"`
- `user_path`: 
    - Path to directory where output file will be placed, e.g. `"/projects/my-public-bucket/VEDA-PEC/results"`
- (OPTIONAL) `output_maap_url`: 
    - Final path for program to output result; this combines the previous output arguments provided by users. Users can optionally override this as needed e.g. `f"{user_path}/{name_for_output_file}.{output_format}"`


## Example Usage

For a comprehensive demonstration of how to use FEDS-PEC, users are advised to view the `demos` directory, which contains the following files:
- `US_2018_TO_2021_ANALYSIS_RUN.ipynb`
    - FEDS Dataset: `public.eis_fire_lf_perimeter_archive`
    - Reference Datset: `InterAgencyFirePerimeterHistory_All_Years_View`
- `CALFIRE_ALL_PERIMS_DEMO.ipynb`
    - FEDS Dataset: `public.eis_fire_lf_perimeter_archive`
    - Reference Datset: `california_fire_perimeters_all`
- `CAMP_DEMO_FEDS_Outline.ipynb`
    - FEDS Dataset: `public.eis_fire_lf_perimeter_archive`
    - Reference Datset: `InterAgencyFirePerimeterHistory_All_Years_View`
- `KINCADE_DEMO_FEDS_Outline.ipynb`
    - FEDS Dataset: `public.eis_fire_lf_perimeter_archive`
    - Reference Datset: `InterAgencyFirePerimeterHistory_All_Years_View`
- `NRT_QUARRY_DEMO.ipynb`
    - FEDS Dataset: `public.eis_fire_lf_perimeter_nrt`
    - Reference Datset: `WFIGS_current_interagency_fire_perimeters`
- `NRT_US_DEMO.ipynb`
    - FEDS Dataset: `public.eis_fire_lf_perimeter_nrt`
    - Reference Datset: `WFIGS_current_interagency_fire_perimeters`

## Key Files and Directories

- `Input_VEDA.py`: A class representing a dataset input from VEDA, which can be sourced from the VEDA API or a predefined path in the MAAP environment.
- `Input_Reference.py`: A class representing a dataset input from a predefined source (e.g., NIFC interagency perimeters) or a user input sourced from a MAAP path.
- `Output_Calculation.py`: A class representing the output for each combination of Input_VEDA and Input_Reference, responsible for calculations and capable of printing, plotting, and serializing data.
- `Utilities.py`: Miscellaneous functions for various operations.
- `/blank`: directory containing the blank outline ipynb, suggested for quickstart use
- `/demos`: directory containing demo ipynb, showcasing use cases along with example outputs
- `/misc`: directory containing additional helper files

## Stability and Development

For reliable performance and validation, users are advised to strictly remain on the `FEDS-PEC-Protected` branch. For experimental/non-stable features and active development, users can consult the `dev` branch at their own discretion. Only finalized features are released and merged into the `FEDS-PEC-Protected` branch after testing.

## Reporting Issues and Submitting Feedback

For any bug/issues, users are encouraged to open a github issue on the official FEDS-PEC github, linked here: https://github.com/ksharonin/feds-benchmarking/issues

## Contact Information

For direct contact regarding matters on contributions, support, feedback, or reporting issues, please email Katrina Sharonin at katrina.sharonin@nasa.gov (alternative email: ksharonin@berkeley.edu).

Thank you for using FEDS-PEC to streamline your geospatial data evaluations and comparisons. We welcome your feedback and contributions to help make this module even more powerful and user-friendly.

## Acknowledgments


