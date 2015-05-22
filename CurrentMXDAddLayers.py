#!/usr/bin/env python
# -*- coding: utf-8 -*-
# CurrentMxdAddLayers.py
# Created: 2014-12-18 @ 16:50:26PM
# Author: Dirk

import os
import arcpy

try:
    from NG911_Config import currentPathSettings
except:
    print "Failed to import settings from NG911_Config."

gdbLocation = currentPathSettings.gdbPath

gdbFolderParts = os.path.split(gdbLocation)[:-1]

gdbFolder = ""

for gdbFolderPart in gdbFolderParts:
    gdbFolder = os.path.join(gdbFolder, gdbFolderPart)

print "GdbFolder = " + gdbFolder

def addLayersToMxd():
    '''Attempts to add the error reporting layers to the user's current Mxd. Failing that, it adds them to errorReportLayers.mxd'''
    successVariable = 0

    try:
        mxd = arcpy.mapping.MapDocument("CURRENT") # For an mxd on the filesystem, use the mxd's full path instead of "CURRENT".
        successVariable = 1
    except:
        print "Mxd assignment from \"CURRENT\" keyword failed. Using the default mxd for error reporting."
        try:
            mxd = os.path.join(gdbFolder, "errorReports.mxd") # Blank mxd in the same folder as the gdb.
            successVariable = 2
        except:
            print "Mxd unavailable."
            successVariable = 0
    
    if successVariable == 1 or successVariable == 2:
        # We have identified an mxd path to use and can start adding layers to it.
        # Assumes the layers are in the same location as the gdb. -- Might not be a safe assumption.
        lineErrorsLayerPath = os.path.join(gdbFolder, "lineErrors.lyr")
        pointErrorsLayerPath = os.path.join(gdbFolder, "pointErrors.lyr")
        polygonErrorsLayerPath = os.path.join(gdbFolder, "polygonErrors.lyr")
        
        errorLayersList = list()
        errorLayersList.append(lineErrorsLayerPath)
        errorLayersList.append(pointErrorsLayerPath)
        errorLayersList.append(polygonErrorsLayerPath)
        
        firstDataFrame = arcpy.mapping.ListDataFrames(mxd)[0]
        
        for errorLayer in errorLayersList:
            print str(errorLayer)
            inMemoryErrorLayer = arcpy.mapping.Layer(errorLayer)
            arcpy.mapping.AddLayer(firstDataFrame, inMemoryErrorLayer)
    else:
        pass
        
if __name__ == "__main__":
    addLayersToMxd()
    
else:
    pass