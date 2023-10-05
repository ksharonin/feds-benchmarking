# Documentation: VEDA Polygon Evaluation and Comparison (PEC)

Author: Katrina Sharonin

## Statement of Need

* What: The VEDA PEC is an add-on to the NASA MAAP platform designed to accelerate comparison of VEDA data sets with reference datasets
    * Reference datasets can be a predefined option (i.e. already saved to a URL in MAAP) or can be user uploaded/defined
    * Calculations include: Ratio, Accuracy, Precision, Recall, IOU, F1, and Symmetric Ratio
    * Currently most support exists for the firenrt perimeter collection; seeking community feedback for new datasets
    * Dumps outputs in convenient formats for research uses and archiving
* Why: rather than force users to re-implement comparisons/calculations on their own for research, this add-on quickly lets users feed in datasets of interest and pump out analysis. More time can be spent on dataset selection and output analysis, rather than implementing/testing software
* Who: MAAP users and Earth science research community

## Installation Instructions
1. Conda enviornment: please run the env-feds bash script to generate the `env-feds` conda enviornment
    * Required packages: glob, sys, logging, pandas, geopandas, pyproj, owslib, datetime, functools, boto3, fsspec, matplotlib
    * TODO: make a bash/conf script for this repo to install
2. Edit/Make a copy of the `BLANK_PEC_Outline.ipynb`
3. Make sure the selected ipynb kernel is the `env-feds` enviornment (and/or
4. Follow instructions in the notebook for quickstart; you only need to modify inputs in the section `User Inputs for Comparison: time, bbox, VEDA set, reference set` 
5.  

## Example Usage: 
* See `DEMO_PEC_Outline.ipynb` for a full demonstration with the Kincade Fire

Functionality documentation: Is the core functionality of the software documented to a satisfactory level (e.g., API method documentation)?

Automated tests: Are there automated tests or manual steps described so that the functionality of the software can be verified?


## Key Files/Classes
* `Input_VEDA.py`: class representing a dataset input from VEDA either from API or a hard-coded path in the MAAP enviornment
* `Input_Reference`: class representing a dataset input from a predefined source (e.g. NIFC interagency perimeters) or a user input sourced from a MAAP path
* `Output_Calculation.py`: class representing an output for each Input_VEDA and Input_Reference run together; holds calculations and capable of printing/plotting/serializing data
* `Utilities.py`: misc functions for various operations
* `PEC_Outline.ipynb`: notebook demonstrating how to set up inputs and use class, assumes user has NASA MAAP acccess
* `PEC_Scratchwork.ipynb`: misc work

## Contribution/Reporting
* Contact ksharonin@berkeley.edu / katrina.sharonin@nasa.gov for support/issues/feedback
 
