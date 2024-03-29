# QGIS Archaeology Resources

This repository contains QGIS symbol sets, SVG files, layout templates, and color palettes for archaeological applications. Most of these resources were created by me, but some of them were created by others who have granted me permission to include them here. As such, the contents of this repository are covered by multiple licenses.

This repository follows the structure required by the popular QGIS plugin [QGIS Resource Sharing](https://plugins.qgis.org/plugins/qgis_resource_sharing/), so QGIS users should be able to access this repository using that plugin.

## Licensing
This repository is currently covered by two licenses:

- `LICENSE.sourcessvgs.md`:  covers the contents of the directory `/collections/Sources/svg`
- `LICENSE.othercontents.md`: covers all other contents of this repository

## Compatibility
The symbol sets in this repository are compatible with QGIS versions 3.16 and later.

## Usage
To access this repository from the QGIS Resource Sharing plugin, follow the steps below (may differ slightly depending on OS and QGIS version):

1. In the Resource Sharing plugin window, go to `Settings > Add repository`, enter the URL https://github.com/josephburkhart/QGIS-Archaeology-Resources.git, give it a name (e.g., 'Archaeology Resources'), and click `OK`.
2. If the repository was successfully added, go to `All Collections` and search for "archaeology" or similar to bring up the collections from this repository.
3. Click `Install` to download and install the collections you want.
4. The symbols in the installed collections should now be visible in your Style Manager. SVGs can be accessed from the standard SVG search widget shown in the Layer Properties window at `Symbology > SVG symbol`.
5. To update your installed collections to match the current version of this repository, in the Resource Sharing plugin window go to `Installed Collections` and click `Reinstall`.

## Contents
This repository contains the following collections: BCAB and Sources.

### BCAB
This collection contains resources that satisfy the mapping requirements of the [BC government's Archaeology Branch](https://www2.gov.bc.ca/gov/content/industry/natural-resource-use/archaeology). The contents are summarized below:

- `symbol`: QGIS symbols (XML format) matching the symbols given in the Archaeology Branch's [Mapping & Spatial Requirements (V.4) [June 23, 2021]](https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/natural-resource-use/archaeology/forms-publications/mapping_and_spatial_requirements.pdf)

### Sources
This collection contains resources that satisfy internal mapping standards at [Sources Archaeological and Heritage Research, Inc](www.sourcesarch.com). The contents are summarized below:

- `color`: standard color palette (GIMP Palette Format - can be imported into QGIS)
- `layout`: QGIS layout template files (letter/tabloid sizes, landscape/portrait orientations, with/without inset maps)
- `project`: QGIS project template files (municipal and forestry)
  - Note: these must be added to the user's project template folder before they can be used as templates. To find the project template folder for your current QGIS user profile, go to `Settings > Options > General > Project Files > Template Folder`.
- `svg`: SVG image files for use as symbols in QGIS
  - Note: the files in this directory are licensed differently from all other files in this repository.
- `symbol`: QGIS symbols (XML format) that match symbols commonly used in Sources maps

### Joseph
This collection contains various python scripts that I use in personal archaeological work. The contents are summarized below:

1. `create-small-grid.py`: This script takes an input layer and generates a small n x n grid inside each input layer feature. Each output grid cell is given a unique grid ID value that includes the parent input feature's grid ID. This script was used to create the minor reference grid in my Master's thesis.
2. `clean-grid-cell-location-list.py`: This script takes a csv file of intersections between two layers and condenses the labels in one column into a list based on duplicate values in another column. It then sorts the lists by ascending feature ID values.
3. `sort-long-grid-cell-location.py`: This script sorts long-form grid cell location IDs by row, column, and then number.
4. `shorten-grid-cell-location.py`: This script takes a list of long-form grid cell IDs and abbreviates them to a more human-readable format.
5. `max-side-length.py`: This script takes a polygon feature and calculates the length of the longest side. (Intended for use in the QGIS Field Calculator.)
6. `top-left-rotation.py`: This script takes a polygon feature and calculates the angle of its top-left side. (Intended for use in the QGIS Field Calculator.)
7. `calculate-utm-coordinates.py`: This script takes a vector layer, calculates the utm Easting and Northing for each feature, and adds that information to the feature's metadata under a new field.
8. `calculate_hard_ties.py`: This script takes a vector layer (features) and a selected point (reference point), and then creates hard-ties for each feature. Each hard-tie has a description field that specifies the distance and bearing (relative to True North) from the reference point to the feature.