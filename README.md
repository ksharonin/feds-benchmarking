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

FEDS-PEC eliminates the need for users to recreate/repeat solutions when conducting geospatial data evaluations. By leveraging this module, researchers and analysts can focus their efforts on dataset selection and analysis, rather than spending time implementing and testing software for comparisons and calculations.

### Who Can Benefit from FEDS-PEC?

FEDS-PEC is primarily aimed at users of the NASA Making Earth System Data Records for Use in Research Environments (MAAP) platform and the broader Earth science research community.

## Installation Instructions

To install and use FEDS-PEC, follow these steps:

1. **Conda Environment Setup:** Run the `env-feds.sh` shell script to create the `env-feds` Conda environment.

2. **Notebook Setup:** Edit or make a copy of the `BLANK_FEDS_Outline.ipynb` located in the `blank` directory.

3. **Kernel Selection:** Ensure that the selected Jupyter Notebook kernel is the `env-feds` environment.

4. **Quickstart:** Follow the instructions in the notebook, specifically the "User Inputs for Comparison" section, to get started.

## Example Usage

For a comprehensive demonstration of how to use FEDS-PEC, refer to the ipynbs located in the `demos` directory, such as the `KINCADE_DEMO_FEDS_Outline.ipynb` notebook, which includes a demonstration using the Kincade Fire dataset.

## Acceptable Input Settings
Acceptable inputs are the scope of inputs that FEDS PEC is designed to accept. This section describes acceptable inputs for FEDS and reference datasets. An acceptable input may be implemented or unimplemented (marked with [NOT IMPLEMENTED])

### FEDS Acceptable Input Settings
- 

### Reference Acceptable Input Settings
- 

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