# README: FEDS Benchmarking Algorithm Development

# Deprecated: NASA MAAP - EIS FIRE FEDS Benchmark Design Doc
Author: Katrina Sharonin
Description: The benchmarking capability of NASA MAAP measures the output product accuracy. Output products include perimeter, burned area, and other forms of "predictions". Sources e.g. NIFC Feature service and FTP Incident files. Must be expandable to additional sources and compatible with current MAAP run algorithm.
Key terms: *Output* (FEDS outputs e.g. perimeters, burned area), *Source* (external sources for accuracy e.g. NIFC, ArcGIS), *Overlay* (resulting object comparing Output v.s. Source)

----

Strategy: 
* OOP implementation of:
* Modulation of performed operations
* Ability to interface with existing outputs of the FEDS algorithm 
* Ability to interface with overlay (outputs of benchmarking); able to save/archive/retrieve on-demand
* Static (globally shared among all class instances) vs. Instance (individual among instances) design
* Ouputs easy to read/access for paper production/publications

Output + Source --> Overlay object --> Visualization, analysis, *storage/persistence*

Key Challenges:
* Appropriate persistence and access to stored overlays
* Compatability with current FEDS implementation
* Outside source access/download
* Level of generalization for outside source access
* Some sources do not have a visual locs interaction --> requires more tedious filtering

Key Questions:
* Defining classes for objects Output and Source? (answer: likely needed)
-> Output is uniform and mainly consistent already
-> Source class would help to generalize any input
-> likely needed to help generalize behavior
* Accessibility of outputs to stakeholders?
-> Want to visualize outputs and performance <--> have the ability to display Overlay object as a geometry with CRS, valid shape, etc. <--> Overlay behaves simiilar to FireObj.py defined by MAAP
* How to store *connections* between the producted Overlay Object and its input Source and Output? 
-> Don't want to waste energy re-generating objects -> but need to somehow retrieve them
-> Possible dictionary of general fires with locs -> if seen before don't add new?
-> Is this connection necessary?
    -> When retrieving Overlay we *obviously* need to know what is was generated from
    -> Likely will used bbox/locs to get <--> need to preserve connection
* CRS ettiqute? Current expectations in MAAP?

Files:
- `benchmark-pseudo.py`: pseudo code implementation of design
- `main.py`: runs benchmarking access, interfaces with FEDS outputs
- `benchmarkConsts.py`: global constants between all files
    -> Default source links
    -> aws `s3` bucket locations of polygon overlays for country/state/GACC (?)
- `overlayObj.py`: overlay object class
- `sourceObj.py`: source object class
- `outputObj.py`: FEDS output object class
- 

----

## 1. Classes and Data Structures

**OutputObj.py**
- Class representing general output from FEDS, key input to produce Overlay objects
- Caution with size (i.e. apply to fire perims, not VIIRS fire detections directly)

Static:
-> All `FireConsts.py` carry overs
Instance:
-> `datetime`: date and time
-> `locs`: generalized coordinates 
-> `bbox`: bounding box generated from `locs` (*NOTE* if a point, must form a valid geom or else shapely fails), main form of filtering
-> `crs`: identified Coordinate System projection of object, needed for country/state/territory i.d.
-> `estimatedCountry`: country of output using overlay with polygons
-> `estimatedGACC`: estimated GACC to generalize terrirtory of Output; used for FTP refinement, but could also compare with additional sources using specific states (?)
    --> OR alternatively: `estimatedState`
    --> Non U.S. considerations? --> `if nonUS then estimatedCountry`
    --> This refinment would really be centered for US but bbox is a fallback
-> `comparisonData`: data of interest to compare for, the most varyig:
    --> e.g. for VIIRS: FRP, confidence
    --> fperim: just perim
    --> burnedArea: area value
    --> burnedNBDT: raster values of severity (what system/thresholds)

**SourceObj.py**
- Class representing general source from outside resource (i.e. HTML FTP access, ArcGIS Feature Service)
- Able to generalize key sources such that future inputs are easy to connect
- Key abilities: can be requested/pinged for status, can intake locs for search

Static:
-> 
Instance:
-> `sourceName`: name of source e.g. FTP, NIFC_ArcGIS, etc. -- should be distinguishable if multiple databases are owned by stakeholders
-> `sourceType`: generalize type of source into categories to sort treatment: `html`, `aws`, `local` (?)
-> `sourceURL`: default as `None`, if `html` type 
    --> must be able to distinguish between types for appropriate handling
-> `datetime`: date and time of source (note needs to be dist of big server vs. indiv poly)

**OverlayObj.py**
- Class representing Overlay of the output and source
- Property access for measures such as calculated accuracy, estimated GACC, etc.

Static:
-> `overlayDatabase`: master link/connection to overlay database persistence location
Instance:
-> `overlayAccuracy`: return calculated accuracy (property access func, see algorithms)
-> `outputHash`: want to connect to original Output object for access
    --> V.s. redundant quality storage
-> `sourceHash`: want to connect to original Source object for access


## 2. Algorithms and Sub-Algorithms

(Broken by class)

**SourceObj.py**
- `readSource`: generalized reading function, depending on type must recruse down
    -> `readSourceFTP`: specific NIFC fit
    -> `readSourceArcService`: fit for ArcGIS services; will rely on key consistent qualities of ???
    -> `readS3Bucket`: read general `s3` url for access; use STAC API for read only attempts if possible
    -> `readGlobFireData`: Yang rec https://www.nature.com/articles/s41597-019-0312-2 
    -> Other: *Must research external sources*
- `sourceType`: return idetified source type which impacts parameter handling (s3 vs. html etc.)
- `filterSource`: quality check on source, *would be highly varying*
- `manualFixes`: quality filter created by user (e.g. remove specific FIDs not caught by automation)

**OutputObj.py**
- `findGACCRegion`:
- `findBestSource`:

**OverlayObj.py**
- `calculateAccuracy`:
- `overlayAccuracy`: return instance calculated accuracy
*What accuracy stats wanted?*
- `plotComparison`: plot the output v. source using gdf conections


## 3. Persistence

Overlay Object Storage
* Must persist **performance** of Overlay 
    -> Stats needed, visualization highly desired
* Must maintain connections between Output + Source which generated the Overlay object
    -> Store Output 
    -> **What if output isn't just a shape, but with raster qualities i.e. cell weights?**
* Ultimately relationships matter --> GDF

EX: Overlay trait GDF table
| Overlay FID | CRS  | bbox | Assoc. Output | Assoc. Source | Performance |
| --- |---| ---|
| ID | Projection | bbox for both output and source | Path to output gdf | Path to source gdf| misc. performance data in dict form |

## 4. Rough Workflow
- Archived/non-NRT fperim
    -> *const to pick selected source*
    -> Time range + region
    -> if source not there in gdf, import in by region based exteral source
    -> if imported in, perform all quality checks
    -> Per fire (fperim) query source 
    -> Overlay fperim vs. source 
    -> Calculate statistics
    -> Store in Gdf table (CRS, bbox for region, path to output, path to source)
- NRT fperim
    -> 
- Fetching on-demand
    -> Per Overlay GDF entry: 
    -> Able to get statistics
    -> Visualize overlay with gdf connection
