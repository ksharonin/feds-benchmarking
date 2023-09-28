# README: VEDA Polygon Evaluation and Comparison (PEC)

Author: Katrina Sharonin

## Quick-Start
* It is highly recommended to read the `Key Files/Classes` section below
* Refer to `PEC_Outline.ipynb` for step-by-step demo

## Key Files/Classes
* `Input_VEDA.py`: class representing a dataset input from VEDA either from API or a hard-coded path in the MAAP enviornment
* `Input_Reference`: class representing a dataset input from a predefined source (e.g. NIFC interagency perimeters) or a user input sourced from a MAAP path
* `Output_Calculation.py`: class representing an output for each Input_VEDA and Input_Reference run together; holds calculations and capable of printing/plotting/serializing data
* `Utilities.py`: misc functions for various operations
* `PEC_Outline.ipynb`: notebook demonstrating how to set up inputs and use class, assumes user has NASA MAAP acccess
* `PEC_Scratchwork.ipynb`: misc work
 
