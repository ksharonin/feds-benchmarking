---
title: 'FEDS-PEC: A Python Library for Streamlining WildFire Perimeter Research'
tags:
  - Python
  - wildfire
  - fire perimeter
  - NASA
authors:
  - name: Katrina Sharonin
    orcid: 0000-0000-0000-0000
    equal-contrib: true
    affiliation: 1
  - name: Author Without ORCID
    equal-contrib: true # (This is how you can denote equal contributions between multiple authors)
    affiliation: 2
  - name: Author with no affiliation
    corresponding: true # (This is how to denote the corresponding author)
    affiliation: 3
affiliations:
 - name: NASA Goddard Space and Flight Center
   index: 1
 - name: Institution Name, Country
   index: 2
 - name: Independent Researcher, Country
   index: 3
date: 16 November 2023
bibliography: paper.bib

# Optional fields if submitting to a AAS journal too, see this blog post:
# https://blog.joss.theoj.org/2018/12/a-new-collaboration-with-aas-publishing
aas-doi: 10.3847/xxxxx <- update this with the DOI from AAS once you know it.
aas-journal: Astrophysical Journal <- The name of the AAS journal.
---

# Summary

The Fire Event Data Suite-Polygon Evaluation and Comparison (FEDS-PEC) is a specialized Python library tailored to accelerate numerical comparison of variable fire perimeters mapping methods. The library is catered to run on the NASA Multi-Algorithm and Analysis Platform (MAAP) and to compare user-selected polygons against fire perimeters from key stakeholder agencies (NIFC, CALFIRE, and WFIGS). The library specializes in comparing NASA’s FEDS fire perimeter product with agency datasets to generate long-term performance assessment and assist NASA researchers in identifying areas of needed improvement in the FEDS algorithm. Although specialized for FEDS, users can freely adapt the library for custom inputs, enabling custom wildfire research.

FEDS-PEC’s core functionality enables seamless access and numerical analysis via simple user parameter settings and minimal code writing. Inputs include datasets of choice, region/bounding box, start time, end time, and day search range. The library visits the requested datasets, applies the region and search times, and performs diverse calculations including ratio, accuracy, precision, recall, IOU, F1 score, and symmetric ratio. Finally, FEDS-PEC returns the polygon metadata and corresponding calculations. Users can interact with the output by plotting the identified polygons and analyzing calculated values.

Overall, FEDS-PEC optimizes evaluation processes, empowering researchers and analysts to efficiently assess perimeter geospatial data without reinventing evaluation solutions. Designed for compatibility with Jupyter Notebooks and offering flexible options, FEDS-PEC strives to bridge the gap between the wildfire research community and firefighting agencies by producing direct calculations and visualizations against various mapping methods.


# Statement of need

Over the past two decades, wildfires in the Western U.S. have increased in severity, frequency, and size [Dennison et al, Weber et al]. Paired with the expansion of the wildland-urban interface [Readeloff et al, Hammer et al], estimated national wildfire damage costs on an annualized basis range from $63.5 billion to $285.0 billion [Thomas et al]. In addition, between 1901-2011, 674 civilian wildfire fatalities occurred in North America [Haynes et al USDA]. California wildfires have claimed 150 lives over the past 5 years alone [CAL FIRE top 20] and over 30% of total U.S. wildland firefighter fatalities from 1910-2010 [Haynes et al USDA].

With the growing risk to property and livelihood in the U.S., precise and efficient methods of tracking active fire spread are critical for supporting near real-time firefighting response and wildfire management decision-making. Several map-making methods are practiced by firefighting agencies to track fire size and location. Primary methods include GPS-walking, GPS flight, and infrared image interpretation [NIFC 2022 Wildfire Perimeter Map Methods]. The latter method, infrared imaging (IR), is one of the most widely demanded due to daily data delivery for routine briefings and synoptic coverage; between 2013 and 2017, yearly IR requests for the USDA Forest Service’s National Infrared Operations Program (NIROPS) increased from about 1.4k to just over 3.0k [USFS NIROPS Poster]. However, aerial infrared imaging methods involve several acquisition challenges, including (A) cost, (B) sensor operation restrictions, (C) limited ability to meet coverage demand, and latency.

Among NASA’s existing projects and tools, the development of thermal remote-sensing via satellites stands as a major potential augmentation to wildfire operations and mapping. The Moderate Resolution Imaging Spectroradiometer (MODIS) aboard the Aqua and Terra satellites, and the Visible Infrared Imaging Radiometer Suite (VIIRS) aboard S-NPP and NOAA 20 (formally known as JPSS-1), represent the primary tools for NASA’s wildfire remote-sensing initiatives. 
Satellite observations are harnessed to generate finalized fire perimeter products. One leading perimeter algorithm is the Fire Event Data Suite Fire Perimeter Dataset (FEDS Fire Perimeters) led by Yang Chen et al. [TODO: describe FEDS algorithm which is sourced from VIIRS ]

The integration of satellite products can address several issues faced by standard IR missions: satellites are not manned and therefore do not pose a safety risk when deployed, satellites do not impede in Fire Traffic Area (FTA), there is a standard temporal resolution for every instrument, tools can provide real-time data, data processing, interpretation, and access can be handled by programs such as NASA FIRMS, there is a fixed cost associated with only creation and maintenance of the satellite tool, and nationwide to global coverage potential.

However, the integration of satellite observations has been limited due to the various issues cited by USFS, including resolution scale (i.e. 2 km for MODIS), false positives, limited swath width, analysis support, latency, post-processing of data, and temporal resolution (6). Overall, USFS deems satellites most appropriate for strategic intelligence rather than tactical incident awareness and assessment (IAA), where IAA focuses on detailed intelligence on “fast moving dynamic fires” and strategic focuses on a wider operating picture (8):

“Strategic Intelligence Mission Description: Maintain a Common Operating Picture to provide situational awareness of fires nationwide. [Technology:] Satellite IR data, fire perimeters, resources, etc. [Definition:] Inform strategic decisions (non-tactical). Prioritize response and resources. Satellite detection may be best [used] for nationwide coverage. Combine with additional data from other sources (i.e GEOMAC).”

Despite various challenges, emerging research and products continue to improve and demonstrate the strength of satellite imagery for wildfire applications. To demonstrate the robustness of satellite perimeter products, there is a need to numerically compare satellite products with current agency mapping methods. By directly overlaying sources, both researchers and firefighting agencies can objectively assess and visualize performance. Most researchers generate their own scripts to perform these calculations. FEDS-PEC, originally created for the FEDS algorithm, is designed to reduce redundancy and provide researchers with a quick-start toolkit to compare fire perimeter datasets.

# Statement of the Field

FEDS-PEC is targeted towards MAAP and FEDS for NASA research, but can also be used for external research for custom user inputs and datasets. In addition, included DEMO jupyter notebooks highlight how to interact with the library and walkthrough the classes.

# Mathematics

Single dollars ($) are required for inline mathematics e.g. $f(x) = e^{\pi/x}$

Double dollars make self-standing equations:

$$\Theta(x) = \left\{\begin{array}{l}
0\textrm{ if } x < 0\cr
1\textrm{ else}
\end{array}\right.$$

You can also use plain \LaTeX for equations
\begin{equation}\label{eq:fourier}
\hat f(\omega) = \int_{-\infty}^{\infty} f(x) e^{i\omega x} dx
\end{equation}
and refer to \autoref{eq:fourier} from text.

# Citations

Citations to entries in paper.bib should be in
[rMarkdown](http://rmarkdown.rstudio.com/authoring_bibliographies_and_citations.html)
format.

If you want to cite a software repository URL (e.g. something on GitHub without a preferred
citation) then you can do it with the example BibTeX entry below for @fidgit.

For a quick reference, the following citation commands can be used:
- `@author:2001`  ->  "Author et al. (2001)"
- `[@author:2001]` -> "(Author et al., 2001)"
- `[@author1:2001; @author2:2001]` -> "(Author1 et al., 2001; Author2 et al., 2002)"

# Figures

Figures can be included like this:
![Caption for example figure.\label{fig:example}](figure.png)
and referenced from text using \autoref{fig:example}.

Figure sizes can be customized by adding an optional second parameter:
![Caption for example figure.](figure.png){ width=20% }

# Acknowledgements

We acknowledge contributions from Brigitta Sipocz, Syrtis Major, and Semyeong
Oh, and support from Kathryn Johnston during the genesis of this project.

# References