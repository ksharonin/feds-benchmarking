# FEDS-PEC (Polygon Evaluation and Comparison) Module Documentation

Author: Katrina Sharonin

## Introduction

Welcome to the Fire Event Data Suite - Polygon Evaluation and Comparison (FEDS-PEC) module. FEDS-PEC is a Python library designed to facilitate benchmarking and evaluation of geospatial data, specifically tailored for FEDS fire perimeters. This module allows users to compare these fire perimeters with reference datasets and perform various calculations, including ratio, accuracy, precision, recall, IOU (Intersection over Union), F1 score, and symmetric ratio. The primary goal of FEDS-PEC is to streamline the process of conducting such evaluations, saving time for researchers and analysts. This README provides detailed information on how to install, use, and contribute to the FEDS-PEC module.

## Statement of Need

### What is FEDS-PEC?

FEDS-PEC is a specialized Python module designed for geospatial data analysis, specifically tailored for FEDS fire perimeters. It offers the following key features:

- Seamless interaction through Jupyter Notebooks (e.g., `BLANK_PEC_Outline.ipynb`).
- The flexibility to use predefined reference datasets or user-uploaded/defined datasets.
- A wide range of calculations, including ratio, accuracy, precision, recall, IOU, F1 score, and symmetric ratio.
- Dedicated support for fire perimeter data, with plans to expand support for additional datasets based on community feedback.
- Convenient output formats for research and archival purposes.

### Why Use FEDS-PEC?

FEDS-PEC eliminates the need for users to recreate/repeat solutions when conducting geospatial data evaluations. By leveraging this module, researchers and analysts can quickly and efficiently compare the FEDS fireperimeter dataset against a reference data set of their choosing. Users can focus their efforts on dataset selection and analysis, rather than spending time implementing and testing software for comparisons and calculations.

### Who Can Benefit from FEDS-PEC?

FEDS-PEC is primarily aimed at users of the NASA Multi-Algorithm and Analysis Platform (MAAP) platform and the broader Earth science research community.

## Installation Instructions

To install and use FEDS-PEC, follow these steps:

1. **Conda Environment Setup:** Run the `env-feds.sh` shell script to create the `env-feds` Conda environment. (NOTE: do not instantiate your conda enviornment in a git repository, you will crash the MAAP enviornment due to memory usage) 

2. **Notebook Setup:** Edit or make a copy of the `BLANK_FEDS_Outline.ipynb` located in the `blank` directory.

3. **Kernel Selection:** Ensure that the selected Jupyter Notebook kernel is the `env-feds` environment.

4. **Quickstart:** Follow the instructions in the notebook, specifically the "User Inputs for Comparison" section, to get started.

## Input Settings
This section describes inputs for FEDS and reference datasets and acceptable values. Some input options may be implemented or unimplemented due to development

### FEDS Input Settings
- `title`: select predefined title sourced from the api, or choose `none` if using a custom local input
    - Implemented:
        - `"firenrt"`: VEDA api fire perimeter dataset
            - See documentation here for full dataset details: https://nasa-impact.github.io/veda-docs/notebooks/tutorials/mapping-fires.html
            - Sept 30th
    - Not implemented:
        - `"none"`
        - `"staging-stac"`
        - `"staging-raster"`

- `collection`: if using a predefined api dataset, choose a corresponding collection, otherwise choose `none` if using a custom local input
    - Implemented:
        - Corresponding title: `"firenrt"`
            - `"public.eis_fire_lf_perimeter_archive"`: collection of historic fire perimeters
    - Not implemented:
        - `"none"`
        - Corresponding title: `"firenrt"`
            - `"public.eis_fire_lf_fireline_archive"`: collection of historic firelines [different from fire perimeters in what way?]
            - `"public.eis_fire_snapshot_fireline_nrt"`: collection of real-time firelines; snapshots are a datastructure that includes smaller fires and a time parameter that represents most recent perimeter circa-given time; time is harder to interpret 
                - Disclaimer: holds perimeters and may repeat calculations
            - `"public.eis_fire_snapshot_perimeter_nrt"`
            - `'public.eis_fire_lf_nfplist_nrt'`,
            - `'public.eis_fire_lf_perimeter_nrt'`: best dataset for time-based queries lf == large fire
            - `'public.eis_fire_lf_nfplist_archive'`,
            - `'public.eis_fire_lf_newfirepix_archive'`,
            - `'public.eis_fire_snapshot_newfirepix_nrt'`,
            - `'public.eis_fire_lf_fireline_nrt'`,
- `access_type`:
    - Implemented: 
        - `api`: the VEDA API is an open-source collection of datasets which includes the FEDS fire perimeter dataset. Select this option for the following titles:
            - `"firenrt"`
            - For more information, please see documentation here: https://nasa-impact.github.io/veda-docs/
    - Not implemented: 
        - `local`: Select this option for datasets manually uploaded by the user. This corresponds with the title `"none"`
        - 
- `limit`: amount of features to consider for FEDS API access; warning appears if it misses any entries; set to `0` for non-api `none` datasets 
- `filter`: `False` or a valid query that compiles with data set e.g. `"farea>5 AND duration>2"`; invalid queries will result in error
- `apply_final_fire`: for `"firenrt`"  set this to `True` if you want the only the latest fireID to be taken per unique FireID, set `False` for other datasets 

### Reference Input Settings

[We need detailed explanations for each input option, and what they mean. For each input: - Where is it coming from, who generated it, what time period does it cover, what spatial range, and what level is the code able to handle it?]

- `title`:
    - Implemented:
        - `"nifc_interagency_history_local`: a static shp datset containing all fire perimeters up to 2021 documented by the National Interagency Fire Center (NIFC) for the United States
            - Agency: National Interagency Fire Center (NIFC)
            - Source: https://data-nifc.opendata.arcgis.com/datasets/nifc::interagencyfireperimeterhistory-all-years-view/explore?location=32.468087%2C-122.087025%2C3.89 
            - Update frequency: downloaded to maap directory once by author
            - Time period covered: 1909 - 2021
            - Geospatial coverage: United States
    - Not implemented:
        - `"WFIGS_current_interagency_fire_perimeters"`: a dynamic shp dataset containing current wildfire perimeters documented by  by the National Interagency Fire Center (NIFC) for the United States; program activately queries the ArcGIS online source
            - Agency: National Interagency Fire Center (NIFC)
            - Source: https://data-nifc.opendata.arcgis.com/datasets/nifc::wfigs-current-interagency-fire-perimeters/explore?location=0.000000%2C0.000000%2C2.48 
            - Update frequency:
            - Time period covered: 
            - Geospatial coverage: United States
        - `"nifc_arcgis_current_incidents_wfigs`
        - `"nifc_arcgis_2023_latest"`
- `control_type`:
    - Implemented:
        - `"defined"`
    - Not implemented:
        - `"custom"`
- `custom_url`
    - Implemented:
        - `"none"`
    - Not implemented:
        - `""`
- `custom_read_type`
    - Implemented:
        - `"none"`
    - Not implemented:
        - `""`
- `filter`: `False` or a valid query that compiles with data set e.g. `"farea>5 AND duration>2"`; invalid queries will result in error

### Shared Input Settings
Inputs shared between FEDS and Reference
- `date start`
    - year, month, day, second, tz_offset_hours, tz_offset_minutes, utc_offset
- `date stop`
    -  year, month, day, second, tz_offset_hours, tz_offset_minutes, utc_offset
- `crs`
- `search bbox`: [top left longitude, top left latitude, bottom right longitude, bottom righ latitude]
- `day_search_range`: x <= 7, used to search for matching reference polygons e.g. if x = 5 FEDS polygon finds an intersecting polygon, but it is 6 days difference in timestamp, it will not be included in the resulting output pairs.

### Output Input Settings
Define format of output and path, all used to construct `output_maap_url` 
- `maap_username`: passed username to write into shared buckets
- `name_for_output_file`: f"firenrt_vs_nifc_interagency_{year_start}_{search_bbox[0]}_{search_bbox[1]}_{search_bbox[2]}_{search_bbox[3]}"
- `output_format`: 
     - Implemented:
        - 
    - Not implemented:
        - `txt`
        - `json`
- `print_on`
    - Implemented:
        - `True`
        - `False`
- `plot_on`
    - Not implemented:
        - `True`


## Example Usage

For a comprehensive demonstration of how to use FEDS-PEC, refer to the ipynbs located in the `demos` directory, such as the `KINCADE_DEMO_FEDS_Outline.ipynb` notebook, which includes a demonstration using the Kincade Fire dataset.

## Testing

FEDS-PEC includes strict argument validation to prevent users from accessing unimplemented features. Unit testing for the module is currently under development.

## Upcoming Features

We have plans to enhance FEDS-PEC with the following features:

- Expanded output formats and improved plotting capabilities.
- Additional predefined datasets for comparison.
- Potential integration of community-shared datasets, allowing non-admin users to upload and share datasets with the public.

## Key Files and Directories

- `Input_VEDA.py`: A class representing a dataset input from VEDA, which can be sourced from the VEDA API or a predefined path in the MAAP environment.
- `Input_Reference.py`: A class representing a dataset input from a predefined source (e.g., NIFC interagency perimeters) or a user input sourced from a MAAP path.
- `Output_Calculation.py`: A class representing the output for each combination of Input_VEDA and Input_Reference, responsible for calculations and capable of printing, plotting, and serializing data.
- `Utilities.py`: Miscellaneous functions for various operations.
- `/blank`: directory containing the blank outline ipynb, suggested for quickstart use
- `/demos`: directory containing demo ipynb, showcasing use cases along with example outputs

## Contribution and Reporting Issues

For contributions, support, feedback, or reporting issues, please contact Katrina Sharonin at ksharonin@berkeley.edu or katrina.sharonin@nasa.gov.

Thank you for using FEDS-PEC to streamline your geospatial data evaluations and comparisons. We welcome your feedback and contributions to help make this module even more powerful and user-friendly.