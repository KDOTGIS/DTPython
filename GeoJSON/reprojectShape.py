#!/usr/bin/env python
# -*- coding: utf-8 -*-
# reprojectShape.py
# Requires GDAL & Python bindings.

# Use this script to reproject shapefiles
# prior to using them in other tools.

try:
    import os
    import sys
    from osgeo import ogr
    from osgeo import osr
except:
    print "Import failed."

# shapefilePath and targetShapefilePath should end in .shp extension.
shapefilePath = r'C:\Python27\DirkScripts\sec\KAMPythonGroup\GeoJSON\polygonTestNAD1983\polygonTestNAD1983.shp'
shapefileProjection = shapefilePath[:-4] + r'.prj'
outputShapefilePath = r''
# Use 4326 for the target projection.


def getWktFromPrj(shapeprj_path):
    prj_file = open(shapeprj_path, 'r')
    prj_text = prj_file.read()
    srs = osr.SpatialReference()
    srs.ImportFromESRI([prj_text])
    del prj_file
    return srs.ExportToWkt()


def reprojectToNewShapefile(startingShapefile, endingShapefile):

    startingProjection = startingShapefile[:-4] + r'.prj'
    
    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(4326) # WGS 84 Lat/Long in decimal degrees.
    
    # Code adapted from the samples found at:
    # http://pcjericks.github.io/py-gdalogr-cookbook/projection.html
    
    driver = ogr.GetDriverByName('ESRI Shapefile')
    
    prj_file = open(startingProjection, 'r')
    prj_text = prj_file.read()
    inSpatialRef = osr.SpatialReference()
    inSpatialRef.ImportFromESRI([prj_text])
    try:
        del prj_file
    except:
        pass
    
    
    # inSpatialRef == outSpatialRef does not return true even if they are the same.
    # Use SRName.IsSame(otherSRName) instead.
    if inSpatialRef.IsSame(outSpatialRef):
        raise('Starting and ending spatial reference are the same. Will not reproject.')
    else:
        print 'Spatial references are not the same, will reproject.'
        pass
    
    coordTransform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)
    
    if endingShapefile == '':
        endingShapefile = startingShapefile[:-4] + '_WGS84.shp'
    else:
        pass
    
    # create the CoordinateTransformation
    coordTrans = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)
    
    # get the input layer
    inDataSet = driver.Open(startingShapefile)
    inLayer = inDataSet.GetLayer()
    
    # create the output layer
    outputShapefile = endingShapefile
    if os.path.exists(outputShapefile):
        driver.DeleteDataSource(outputShapefile)
    else:
        pass
    outDataSet = driver.CreateDataSource(outputShapefile)
    
    startingFeature = inLayer.GetFeature(0)
    
    startingFeatureGeomRef = startingFeature.GetGeometryRef()
    #print startingFeatureGeomRef
    #print dir(startingFeatureGeomRef)
    startingFeatureGeomType = startingFeatureGeomRef.GetGeometryType()
    print ''
    print 'StartingFeatureGeomType = ' + str(startingFeatureGeomType)
    
    
    # Not sure why the shapefile needs a layer, or why
    # that layer needs a name... but that's how the driver seems to work.
    layerToCreate = startingShapefile[:-4]
    layerToCreate = os.path.split(layerToCreate)[-1:][0]
    print layerToCreate
    outLayer = outDataSet.CreateLayer(layerToCreate, geom_type=startingFeatureGeomType) # Seems to work best using the kwarg geom_type.
    
    # add fields
    inLayerDefn = inLayer.GetLayerDefn()
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        outLayer.CreateField(fieldDefn)
    
    # get the output layer's feature definition -- Does this make sense? Should be creating a new shapefile.
    outLayerDefn = outLayer.GetLayerDefn()
    
    # loop through the input features
    inFeature = inLayer.GetNextFeature()
    while inFeature:
        # get the input geometry
        geom = inFeature.GetGeometryRef()
        # reproject the geometry
        geom.Transform(coordTrans)
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
    
    print 'EndingShapefile = ' + str(endingShapefile)
    
    endingProjection = endingShapefile[:-4] + '.prj'
    
    print 'EndingProj = ' + str(endingProjection)
    
    outSpatialRef.MorphToESRI() 
    endingProjHandler = open(endingProjection, 'w') 
    endingProjHandler.write(outSpatialRef.ExportToWkt()) 
    endingProjHandler.close()
    
	# Free memory by removing the references to the data
    del endingProjHandler
    del inDataSet
    del outDataSet
    del startingProjection
    del endingProjection

if __name__ == "__main__":
    reprojectToNewShapefile(shapefilePath, outputShapefilePath)

else:
    pass