#!/usr/bin/env python
# -*- coding: utf-8 -*-
# shapeToGeoJSONviaOGR.py
# Requires GDAL & Python bindings.

# This script does not convert to
# WGS 84 Lat/Long in decimal degrees
# or supply Projection Information.

# Convert the shapefile's projection with
# reprojectShape.py before using this script
# to convert from shapefile to GeoJSON.

try:
    import os
    import sys
    from osgeo import ogr
    from osgeo import osr
except:
    print "Import failed."


# Can be any shapefile extension except .sbx or .shp.xml.
# The shapefile should be in WMS84 lat/long projection -- EPSG(4326)
shapefilePath = r'C:\GIS\Shapefiles\test\railways_WM.shp'
geojsonPath = r'C:\GIS\GeoJSON\railways_WM.json' # Change path to be the same as the KAMPythonGroup file.

def convertToGeoJSON(shapefileLocation, geojsonLocation):
    # Create the input Driver
    inDriver = ogr.GetDriverByName('ESRI Shapefile')
    
    # get the input layer
    inDataSet = inDriver.Open(shapefileLocation)
    inLayer = inDataSet.GetLayer()
    
    startingFeature = inLayer.GetFeature(0)
    
    startingFeatureGeomRef = startingFeature.GetGeometryRef()
    #print startingFeatureGeomRef
    #print dir(startingFeatureGeomRef)
    startingFeatureGeomType = startingFeatureGeomRef.GetGeometryType()
    
    # Create the output Driver
    outDriver = ogr.GetDriverByName('GeoJSON')
    
    # The GeoJSON driver will not overwrite output,
    # so if it exists, it needs to be deleted before
    # we can recreate it.
    if os.path.exists(geojsonLocation):
        outDriver.DeleteDataSource(geojsonLocation)
    else:
        pass
    outDataSet = outDriver.CreateDataSource(geojsonLocation)
    outLayer = outDataSet.CreateLayer(geojsonLocation, geom_type=startingFeatureGeomType)
    
    # add fields
    inLayerDefn = inLayer.GetLayerDefn()
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        outLayer.CreateField(fieldDefn)
    
    # Get the output Layer's Feature Definition
    outLayerDefn = outLayer.GetLayerDefn()

    # loop through the input features
    inFeature = inLayer.GetNextFeature()
    while inFeature:
        # get the input geometry
        geom = inFeature.GetGeometryRef()
        # create a new feature
        outFeature = ogr.Feature(outLayerDefn)
        # set the geometry and attribute
        outFeature.SetGeometry(geom)
        for i in range(0, outLayerDefn.GetFieldCount()):
            outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), inFeature.GetField(i))
        # add the feature to the shapefile
        outLayer.CreateFeature(outFeature)
        # destroy the features and get the next input feature
        outFeature.Destroy()
        inFeature.Destroy()
        inFeature = inLayer.GetNextFeature()

    # close the shapefiles
    inDataSet.Destroy()
    outDataSet.Destroy()
    
    del inDataSet
    del outDataSet

if __name__ == "__main__":
    convertToGeoJSON(shapefilePath, geojsonPath)
    