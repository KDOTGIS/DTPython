#!/usr/bin/env python
# -*- coding: utf-8 -*-
# geoJSONCombination.py

# Uses reprojectShape.py and shapeToGeoJSONViaOGR.py
# to process a shapefile for display in a browser.

# Both of the imported functions require the GDAL
# core components and the GDAL Python bindings.
# Get them here: http://www.gisinternals.com/release.php

from reprojectShape import reprojectToNewShapefile
from shapeToGeoJSONViaOGR import convertToGeoJSON

# lineTestKSSouth
# Input shapefile path
path1 = r'C:\GIS\Python\GeoJSON\lineTestKSSouth\lineTestKSSouth.shp'
# Output shapefile path
path2 = r'C:\GIS\Python\GeoJSON\lineTestKSSouth\lineTestKSSouth_WGS84.shp'
# Output geoJSON path
path3 = r'C:\GIS\Python\GeoJSON\lineTestKSSouth.json'

if __name__ == "__main__":
    reprojectToNewShapefile(path1, path2)
    convertToGeoJSON(path2, path3)

else:
    pass
