#!/usr/bin/env python
# -*- coding: utf-8 -*-
# createnonstateroutes.py
# Created: 2015-02-02
# Updated: 2015-02-03

import os
from arcpy import (CopyFeatures_management, CreateRoutes_lr, Delete_management, Describe, env, FlipLine_edit, 
                   MakeFeatureLayer_management, SelectLayerByAttribute_management, GetCount_management)

inputSystem = r'Database Connections\sdeprod_GIS.sde\SHARED.NON_STATE_SYSTEM'
outputSystem = r'Database Connections\countyMapsSQLSDE.sde\countyMaps.SDE.Non_State_System_Routes'


def buildNonstateRoutes(systemToRoute, routedSystemExport):
    print "Building NonstateRoutes..."
    inMemoryNonStateSystem = r'in_memory\nonStateSystem'
    inMemoryNonStateSystemLyr = "featureClassAsALayer"
    
    # Semi-ugly notation to get the all but the last item from the split output.
    gdb = os.path.split(routedSystemExport)[:-1][0]
    
    print gdb
    
    env.workspace = gdb
    env.outputMFlag = "Enabled"
    
    spatialReferenceToUse  = Describe(systemToRoute).spatialReference
    spatialReferenceToUse.setMDomain(0, 500)
    spatialReferenceToUse.MTolerance = 0.001
    spatialReferenceToUse.MResolution = 0.001
    
    env.outputCoordinateSystem = spatialReferenceToUse
    
    
    try:
        Delete_management("in_memory")
    except:
        print "Can't delete in_memory"
    
    mainWhereClause = "FUNCLASS in (4,5,6,7) AND MILEAGE_COUNTED = -1 AND LENGTH <> 0 AND PROPOSED <> SOMETHING"
    
    loadedNonStateSystem = "loadedNonStateSystem"
    
    # Loads the systemToRoute as loadedNonStateSystem
    MakeFeatureLayer_management(systemToRoute, loadedNonStateSystem, mainWhereClause)
    
    debugFeatureCount = GetCount_management(loadedNonStateSystem)
    
    print "Total loaded rows = " + str(debugFeatureCount)
    
    CopyFeatures_management(loadedNonStateSystem, inMemoryNonStateSystem)
    
    del loadedNonStateSystem
    
    debugFeatureCount = GetCount_management(inMemoryNonStateSystem)
    
    print "Total copied rows = " + str(debugFeatureCount)
    
    MakeFeatureLayer_management(inMemoryNonStateSystem, inMemoryNonStateSystemLyr) # Needed to use select by attribute.
    
    lrsBackwardsWhereClause = "LRS_BACKWARDS = -1"
    
    SelectLayerByAttribute_management(inMemoryNonStateSystemLyr, "NEW_SELECTION", lrsBackwardsWhereClause)
    
    debugFeatureCount = GetCount_management(inMemoryNonStateSystemLyr)
    
    print "LRS backwards rows = " + str(debugFeatureCount)
    
    # Reverse line direction for selected lines
    # Used on the loaded (to memory) version of the non state system because it modifies the
    # feature class (not the layer, but the feature class it references) in place without output.
    FlipLine_edit(inMemoryNonStateSystemLyr)
    
    SelectLayerByAttribute_management(inMemoryNonStateSystemLyr, "CLEAR_SELECTION")
    
    debugFeatureCount = GetCount_management(inMemoryNonStateSystemLyr)
    
    print "Total (non)selected rows = " + str(debugFeatureCount)
    
    routeIDField = "LRS_KEY"
    measureSource = "TWO_FIELDS"
    beginField = "LRS_BEG_CNTY_LOGMILE"
    endField = "LRS_END_CNTY_LOGMILE"
    
    CreateRoutes_lr(inMemoryNonStateSystemLyr, routeIDField, routedSystemExport, measureSource, beginField, endField)
    
    debugFeatureCount = GetCount_management(routedSystemExport)
    
    print "Total routes written = " + str(debugFeatureCount)
    
    # Delete the loaded in_memory layer.
    del inMemoryNonStateSystemLyr
    
    # Delete the in_memory feature class.
    try:
        Delete_management(inMemoryNonStateSystem)
    except:
        print "Can't delete in_memory\nonStateSystem"
        
    # Delete the variable that referenced the path to the in_memory\nonStateSystem feature class.
    del inMemoryNonStateSystem
    
    ## Might add something to move it into SDEPROD.Shared later, after testing.
    ## Currently need a new LRS key for county roads. Right now, they're basically
    ## all the same LRS key, which is problematic. The entire Non_State_System
    ## has only 5020 different LRS keys -- which is far too few for all of the
    ## possible routes within the state.

if __name__ == "__main__":
    buildNonstateRoutes(inputSystem, outputSystem)