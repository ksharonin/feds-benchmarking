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
date: 16 November 2023
bibliography: paper.bib

---

# Summary

The Fire Event Data Suite-Polygon Evaluation and Comparison (FEDS-PEC) is a specialized Python module tailored to accelerate numerical comparison of variable fire perimeters mapping methods. The module is catered to run on the NASA Multi-Algorithm and Analysis Platform (MAAP) and to compare NASA’s FEDS fire perimeter product against fire perimeters from key stakeholder agencies (e.g. NIFC, CALFIRE, and WFIGS) along with user-inputted datasets. Ultimately FEDS-PEC is aimed at generating long-term performance assessments and assisting NASA researchers in identifying areas of needed improvement in the FEDS algorithm. Although specialized for FEDS, users can freely adapt the library for custom perimeter versus perimeter comparisons, enabling wildfire research. FEDS-PEC’s core functionality enables seamless access to multiple APIs and datasets along with numerical analysis. This is accomplished by providing template notebooks with which users can compare different databases of fire perimeters from a common syntax. Inputs include datasets of choice, region/bounding box, start time, end time, day search range and filters. The library visits the requested datasets, applies the region and search times, and performs diverse calculations including ratio, accuracy, precision, recall, IOU, F1 score, and symmetric ratio difference. Finally, FEDS-PEC returns the polygon metadata and corresponding calculations. Users can interact with the output by plotting the identified polygons and analyzing calculated values.

Overall, FEDS-PEC optimizes evaluation processes, empowering researchers and analysts to efficiently assess perimeter geospatial data without reinventing evaluation solutions. Designed for compatibility with Jupyter Notebooks and offering flexible options, FEDS-PEC strives to bridge the gap between the wildfire research community and firefighting agencies by making the evaluation of fire-perimeter products easy, accessible, and frequent.


# Statement of need

Over the past two decades, wildfires in the Western U.S. have increased in severity, frequency, and size @dennison_large_2014, @weber_spatiotemporal_2020. Paired with the expansion of the wildland-urban interface [Readeloff et al, Hammer et al], estimated national wildfire damage costs on an annualized basis range from $63.5 billion to $285.0 billion [Thomas et al]. In addition, between 1901-2011, 674 civilian wildfire fatalities occurred in North America [Haynes et al USDA]. California wildfires have claimed 150 lives over the past 5 years alone [CAL FIRE top 20] and over 30% of total U.S. wildland firefighter fatalities from 1910-2010 [Haynes et al USDA].

With the growing risk to property and livelihood in the U.S., precise and efficient methods of tracking active fire spread are critical for supporting near real-time firefighting response and wildfire management decision-making. Several map-making methods are practiced by firefighting agencies to track fire size and location. Primary methods include GPS-walking, GPS flight, and infrared image interpretation [NIFC 2022 Wildfire Perimeter Map Methods]. The latter method, infrared imaging (IR), is one of the most widely demanded due to daily data delivery for routine briefings and synoptic coverage; between 2013 and 2017, yearly IR requests for the USDA Forest Service’s National Infrared Operations Program (NIROPS) increased from about 1.4k to just over 3.0k [USFS NIROPS Poster]. However, aerial infrared imaging methods involve several acquisition challenges, including cost, sensor operation restrictions, limited ability to meet coverage demand, and latency.
Among NASA’s existing projects and tools, the development of thermal remote-sensing via satellites stands as a major potential augmentation to wildfire operations and mapping. The Moderate Resolution Imaging Spectroradiometer (MODIS) aboard the Aqua and Terra satellites, and the Visible Infrared Imaging Radiometer Suite (VIIRS) aboard S-NPP and NOAA 20 (formally known as JPSS-1), represent the primary tools for NASA’s wildfire remote-sensing initiative.

Satellite observations are harnessed to generate finalized fire perimeter products. One leading perimeter algorithm is the FEDS Fire Perimeters led by Yang Chen et al. This system employs automated processes to aggregate and analyze VIIRS instrument data every 12 hours, identifying active fire pixels and delineating fire perimeters. Using an alpha shape algorithm, it integrates these data points, allowing for a comprehensive and dynamic tracking of fire attributes and shapes over time, facilitating near real-time monitoring of fire progression and characteristics within a region.
The integration of satellite products can address several issues faced by standard IR missions: satellites are not manned and therefore do not pose a safety risk when deployed, satellites do not impede in Fire Traffic Area, there is a standard temporal resolution for every instrument, tools can provide real-time data, data processing, interpretation, and access can be handled by programs such as NASA FIRMS, there is a fixed cost associated with only creation and maintenance of the satellite tool, with nationwide to global coverage potential.

However, the integration of satellite observations has been limited due to the various issues cited by USFS, including resolution scale (i.e. 2 km for MODIS), false positives, limited swath width, analysis support, latency, post-processing of data, and temporal resolution [NWCG 2020]. Overall, USFS deems satellites most appropriate for strategic intelligence rather than tactical incident awareness and assessment (IAA), where IAA focuses on detailed intelligence on “fast moving dynamic fires” and strategic focuses on a wider operating picture. Most importantly, a key goal of the USFS is to: “Continue to evaluate satellite detection and mapping capability” [NWCG 2020 Slide 16].

Despite various challenges, emerging research and products continue to improve and demonstrate the strength of satellite imagery for wildfire applications. To demonstrate the robustness of satellite perimeter products and support firefighting agencies, there is a need to numerically compare satellite products with current agency mapping methods. By directly overlaying sources, both researchers and firefighting agencies can objectively assess and visualize the performance of different fire-measurement techniques. Most researchers generate their own scripts to perform these calculations. FEDS-PEC is designed to reduce redundancy and provide researchers with a quick-start toolkit to compare fire perimeter datasets. By uplifting researcher efficiency, the scientific community can more effectively collaborate with firefighting/stakeholder agencies to identify strengths, weaknesses, and opportunities for improvement.

# Statement of the Field

As of January 2024, to the authors’ best knowledge no other open-source comparison library for fire perimeters  exists. Of note are many spatial tools and packages exist for calculating metrics of spatial matching. Package examples include PySAL [Cite], Shapely [Cite], Geopandas [Cite]. General tool examples include ArcGIS Pro [cite] and QGIS [cite].

Importantly, FEDS-PEC  is not a general spatial calculation package. Instead, it focuses on automating three problems common to fire science: 1) Providing access to different datasets, 2) aligning datasets, or identifying which perimeters from different datasets are likely describing the same fire, even if the perimeters may be from different times, shapes, and resolutions, 3) calculating the spatial agreement between perimeters that represent the same fire. While motivated by fire-research, these three problems may emerge in other fields where events are described by polygons, such as storm-tracking, plume tracking, and landslides.

# FEDS-PEC Project

![Figure 1: Sample result plot comparing a FEDS archive perimeter to a NIFC Archive Reference perimeter from US_2018_TO_2021_ANALYSIS_RUN.ipynb](images/finalized_with_legend_FEDS.jpg)

## Overview

FEDS-PEC will compare vector perimeters from different sources, perform multiple calculation functions, and output numerical and visual results (Figure 1). 

FEDS-PEC requires user inputs of time interval, region, and dataset settings to generate 3 objects: `InputFEDS`, `InputReference`, and `OutputCalculation`. 

`InputFEDS` represents the FEDS perimeter input. `InputReference` represents the stakeholder dataset (e.g. NIFC archive polygon, CAL FIRE historic perimeter, etc). `OutputCalculation` is an object which stores the results of comparing `InputFEDS` and `InputReference`. It will generate verbose outputs that users can subsequently use to plot information. 

## Supported API for FEDS Perimeters
- FEDS perimeters are sourced via a single VEDA API; documentation can be found at [VEDA documentation]. However, only specific collections of the API are supported. See below implemented collections: 
    - public.eis_fire_lf_perimeter_archive
        - Description: Perimeter of cumulative fire-area, from fires over 5 km^2 in the Western United States. Every fire perimeter from 2018-2021.
    - public.eis_fire_lf_perimeter_nrt	
        - Description: Perimeter of cumulative fire-area, from fires over 5 km^2. Every fire perimeter currently present near–real time.


## Supported APIs for Reference Fire Perimeters
- NIFC Open Data: InterAgencyFirePerimeterHistory All Years View
    - Description:
    - Link: https://data-nifc.opendata.arcgis.com/maps/interagencyfireperimeterhistory-all-years-view 
    - ref_title = “InterAgencyFirePerimeterHistory_All_Years_View”
    - Note: This dataset has been predownloaded into a MAAP directory. Should users have access to MAAP and interest in a stable static version of the dataset, use ref_title = “Downloaded_InterAgencyFirePerimeterHistory_All_Years_View”
    - Note: Users can download this dataset via the provided link; select “download” and the “ShapeFile” option. 

[TODO]

## Key Features 

[TODO]

## Directory File Structure

## Calculation Formulas

All calculation formulas can be viewed in `Output_Calculation.py` as python methods.

## Logic and Workflow

![Figure 2: Logic Diagram](images/FEDS_PEC_Logic.drawio (2).png){ height=200px }

## User Set-up Guide

The FEDS-PEC README.md provides detailed instructions for users.

## Reporting Issues and Submitting Feedback

For any bug and issues, users are encouraged to open a github issue on the official FEDS-PEC github, linked here: https://github.com/ksharonin/feds-benchmarking/issues 

# Research Applications: Tentative Results with 2018-2021 United States FEDS VS. NIFC Archive
[TODO]

# Citations

Citations to entries in paper.bib should be in
[rMarkdown](http://rmarkdown.rstudio.com/authoring_bibliographies_and_citations.html)
format.

If you want to cite a software repository URL (e.g. something on GitHub without a preferred
citation) then you can do it with the example BibTeX entry below for @hammer_wildlandurban_2007.

# Acknowledgements

[TODO]
EIS-FIRE, NASA GSFC Pathways program

# References