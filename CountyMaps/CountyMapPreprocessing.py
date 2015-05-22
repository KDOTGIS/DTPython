#!/usr/bin/env python
# -*- coding: utf-8 -*-
# CountyMapPreprocessing.py

# Takes the data from the excel file and puts it into
# an ESRI geodatabase for easier use in other scripts.

# Use a searchcursor to read in the rows here
# and apply them to other data.

# Change this to get data from SDEDEV, not GISPROD.
# In fact, do that for all of the data that you can
# which exists in SDEDEV.
# GISPROD is not very functional for ArcMap Users.


gdbLocation = r'Database Connections\countyMapsSQLSDE.sde' # Change to the countyMaps SQL server instance.
gdbPlusUserSchema = gdbLocation + '\countyMaps.SDE.'
excelSettingsLocation = r'\\gis\Planning\Cart\Maps\MXD\2014_Update\CountyMapDataDrivenSettings.xlsx'

import os
import xlrd
import arcpy
from arcpy import env
import sys
from arcpy.da import SearchCursor as daSearchCursor, InsertCursor as daInsertCursor, UpdateCursor as daUpdateCursor  # @UnresolvedImport @UnusedImport
env.workspace = gdbLocation
env.overwriteOutput = True
env.outputZFlag = "Disabled"


def ImportAllSheets(in_excel, out_gdb):
    workbook = xlrd.open_workbook(in_excel)
    sheets = [sheet.name for sheet in workbook.sheets()]

    print('{} sheets found: {}'.format(len(sheets), ','.join(sheets)))
    sheetCounter = 0
    
    for sheet in sheets:
        # The out_table is based on the input excel file name
        # a underscore (_) separator followed by the sheet name
        if sheetCounter == 0:
            out_table = os.path.join(out_gdb,
                arcpy.ValidateTableName("CountyMapSizes", out_gdb))
    
            print('Converting {} to {}'.format(sheet, out_table))
    
            # Perform the conversion
            arcpy.ExcelToTable_conversion(in_excel, out_table, sheet)
            
        else:
            pass
        
        sheetCounter = sheetCounter + 1
    
    print "Sheet import complete!"


def nonStateAndCountyImport():
    
    # Copy the county polygons and the
    # non_state_system from Oracle.
    
    # Make this part a separate function, and maybe have it delete the table
    # instead of having it write over it.
    
    if arcpy.Exists("Non_State_System_No_Z_County"):
        arcpy.Delete_management("Non_State_System_No_Z_County")
    else:
        pass
    
    if arcpy.Exists("Counties_No_Z"):
        arcpy.Delete_management("Counties_No_Z")
    else:
        pass 
    
    print "Importing the Non_State_System..."
    nonStateSystemToCopy = r'Database Connections\sdedev_GIS_DEV.sde\Shared.Non_State_System' # Change to sdedev
    nonStateSystemOutput = gdbPlusUserSchema + 'Non_State_System_No_Z'
    arcpy.CopyFeatures_management(nonStateSystemToCopy, nonStateSystemOutput)
    
    
    #print "Adding a projection to the imported Non_State_System..."
    #try:
        
        # get the coordinate system by describing a feature class
        #coordinateSystemToAssign = r'\\gisdata\ArcGIS\GISdata\GDB\Lambert_Conformal_Conic_2SP.prj'
        
        # Assign the coordinate system for the NonStateSystem.
        #arcpy.DefineProjection_management(nonStateSystemOutput, coordinateSystemToAssign)
        
    #except arcpy.ExecuteError:
    #    print(arcpy.GetMessages(2))
        
    #except Exception as ex:
    #    print(ex.args[0])
    
    
    print "Importing the Counties..."
    countyPolygonsToCopy = r'C:\Users\dtalley\AppData\Roaming\ESRI\Desktop10.2\ArcCatalog\sdedev_GIS_DEV.sde\Shared.Counties'
    countyPolygonsOutput = gdbPlusUserSchema + 'Counties_No_Z'
    arcpy.CopyFeatures_management(countyPolygonsToCopy, countyPolygonsOutput)
    
    # Shouldn't have to add a projection with data from SDEDEV.
    #print "Adding a projection to the imported Counties..."
    #try:
        
        # get the coordinate system by describing a feature class
        #coordinateSystemToAssign = r'\\gisdata\ArcGIS\GISdata\GDB\Lambert_Conformal_Conic_2SP.prj'
        
        # Assign the coordinate system for the County polygons.
        #arcpy.DefineProjection_management(countyPolygonsOutput, coordinateSystemToAssign)
        
    #except arcpy.ExecuteError:
    #    print(arcpy.GetMessages(2))
        
    #except Exception as ex:
    #    print(ex.args[0])


def countyAndRoadPreprocessing():
    
    
    print "Removing non-County roads..."
    featureClass1 = gdbPlusUserSchema + 'Non_State_System_No_Z'
    featureClass1Out = gdbPlusUserSchema + 'Non_State_System_No_Z_County'
    
    inMemoryRoadsLayer1 = "roadsToCounty"
    
    # Need to delete out the non-county roads.
    arcpy.CopyFeatures_management(featureClass1, featureClass1Out)
    
    # Load the feature class with all non_state roads.    
    arcpy.MakeFeatureLayer_management(featureClass1Out, inMemoryRoadsLayer1)
    # Now select & delete all the roads that do not have 999 as their city number.
    selectionString = "\"CITYNUMBER\" <> 999"
    
    arcpy.SelectLayerByAttribute_management(inMemoryRoadsLayer1, "NEW_SELECTION", selectionString)
    
    countNumber = arcpy.GetCount_management(inMemoryRoadsLayer1)
    
    if countNumber >= 1:
        try:
            arcpy.DeleteFeatures_management(inMemoryRoadsLayer1)
        except Exception as e:
            # If an error occurred, print line number and error message
            tb = sys.exc_info()[2]
            print("Line {0}".format(tb.tb_lineno))
            print(e.message)
    else:
        pass
    
    # Cleanup
    if 'inMemoryRoadsLayer1' in locals():
        del inMemoryRoadsLayer1
    else:
        pass
    
    
    featureClass2 = gdbPlusUserSchema + 'Non_State_System_No_Z_County'
    fieldListForRoads = ["RD_NAMES", "COUNTY_NUMBER"]
    featureClass2Out = gdbPlusUserSchema + 'Non_State_System_No_Z_County_DS'
    
    featureClass3 = featureClass2Out
    featureClass3Out = gdbPlusUserSchema + 'Non_State_System_No_Z_County_Cleaned'
    
    inMemoryRoadsLayer2 = "roadsToDissolve"
    inMemoryRoadsLayer3 = "roadsToClean"
    
    
    print "Dissolving road segments by Name & County..."
    # Load the undissolved feature class.    
    arcpy.MakeFeatureLayer_management(featureClass2, inMemoryRoadsLayer2)
    
    # Dissolve based on RD_NAMES and COUNTY_NUMBER.    
    arcpy.Dissolve_management(inMemoryRoadsLayer2, featureClass2Out, fieldListForRoads, "", 
                          "SINGLE_PART", "DISSOLVE_LINES")
    
    # Cleanup
    if 'inMemoryRoadsLayer2' in locals():
        del inMemoryRoadsLayer2
    else:
        pass
    
    
    print "Deleting unnamed road segments..."
    # Copy the feature class to prepare for deleting unnamed roads.
    arcpy.CopyFeatures_management(featureClass3, featureClass3Out)
    
    # Load the copied feature class.
    arcpy.MakeFeatureLayer_management(featureClass3Out, inMemoryRoadsLayer3)
    
    # Now select & delete all the roads that have <null> or "" as their roadname.
    selectionString = "\"RD_NAMES\" IS NULL OR \"RD_NAMES\" = '' OR \"COUNTY_NUMBER\" = 0 OR \"COUNTY_NUMBER\" >= 106"
    
    arcpy.SelectLayerByAttribute_management(inMemoryRoadsLayer3, "NEW_SELECTION", selectionString)
    
    countNumber = arcpy.GetCount_management(inMemoryRoadsLayer3)
    
    print "For " + selectionString + ", selected = " + str(countNumber)
    
    if countNumber >= 1:
        try:
            arcpy.DeleteFeatures_management(inMemoryRoadsLayer3)
        except Exception as e:
            # If an error occurred, print line number and error message
            tb = sys.exc_info()[2]
            print("Line {0}".format(tb.tb_lineno))
            print(e.message)
    else:
        pass
    
    # Cleanup
    if 'inMemoryRoadsLayer3' in locals():
        del inMemoryRoadsLayer3
    else:
        pass
    
    
    print "Preprocessing for county road label points is complete!"

def countyBuffersAndNon_StateErase():
    print "Now adding county polygon buffers..."
    
    countyPolygonsMain = gdbPlusUserSchema + 'Counties_No_Z'
    countyPolygonsEraseBuffer = gdbPlusUserSchema + 'Counties_No_Z_Erase_Buffer'
    countyPolygonsExtensionBuffer = gdbPlusUserSchema + 'Counties_No_Z_Extension_Buffer'
    
    
    # Hard coded the buffer distance to 11000 instead of calculating based on SQRT_DIV8 field value.
    bufferDistance = 11000
    print "Creating the Extension Buffer"
    arcpy.Buffer_analysis(countyPolygonsMain, countyPolygonsExtensionBuffer, bufferDistance, "FULL", "", "NONE")
    
    print "Creating the Erase Buffer"
    arcpy.Buffer_analysis(countyPolygonsMain, countyPolygonsEraseBuffer, -(bufferDistance), "FULL", "", "NONE")
    
    print "Done adding county polygon buffers!"
    
    print "Starting road feature erase."
    
    xyToleranceVal = "5 Feet"
    featureClass4 = gdbPlusUserSchema + 'Non_State_System_No_Z_County_Cleaned'
    featureClass4Out = gdbPlusUserSchema + 'Non_State_System_For_Point_Creation'
    
    arcpy.Erase_analysis(featureClass4, countyPolygonsEraseBuffer, featureClass4Out, xyToleranceVal)
    
    print "Road feature erase complete!"
    
# Need to create a function that makes a new dataset for bridges that only shows bridges in the counties. -- Should take
# the current bridge datasets (2) and then erase using the city boundaries so that the bridges within city boundaries
# are not shown.


def countyOnlyBridgeExport():
    xyToleranceVal = "5 Feet"
    nonStateBridgeLayerIn = r'Database Connections\sdedev_GIS_DEV.sde\SHARED.NON_STATE_BRIDGES'
    stateBridgeLayerIn = r'Database Connections\sdedev_GIS_DEV.sde\SHARED.GIS_BRIDGE_DETAILS_LOC'
    
    cityPolygons = r'Database Connections\sdedev_GIS_DEV.sde\SHARED.CITY_LIMITS'
    nonStateBridgeLayerOut = r'Database Connections\countyMapsSQLSDE.sde\countyMaps.SDE.County_Non_State_Bridges'
    stateBridgeLayerOut = r'Database Connections\countyMapsSQLSDE.sde\countyMaps.SDE.County_State_Bridges'
    
    # Will contain only Non-State Bridges outside of Cities
    arcpy.Erase_analysis(nonStateBridgeLayerIn, cityPolygons, nonStateBridgeLayerOut, xyToleranceVal)
    
    # Will contain only State Bridges outside of Cities
    arcpy.Erase_analysis(stateBridgeLayerIn, cityPolygons, stateBridgeLayerOut, xyToleranceVal)
    pass


def createCountyLinesForEachCounty():
    
    inputCountyLines = r'Database Connections\sdedev_GIS_DEV.sde\SHARED.COUNTY_LINES'
    inputCountyPolygons = r'Database Connections\sdedev_GIS_DEV.sde\SHARED.COUNTIES'
    dissolvedCountyLines = r'Database Connections\countyMapsSQLSDE.sde\CountyLinesDissolved'
    bufferedCountyPolygons = r'Database Connections\countyMapsSQLSDE.sde\CountiesBuffered'
    loadedCounties = 'loadedCounties'
    tempCountyLines = r'in_memory\tempCountyLines'
    outputCountyLines = r'Database Connections\countyMapsSQLSDE.sde\CountyLinesIntersected'
    bufferCursorFields = ["OBJECTID"]
    
    # Need to dissolve all of those county lines into one set of lines
    # then, need to create 105 features that are are intersected
    # with the polygons from said line dissolve.
    
    arcpy.Dissolve_management(inputCountyLines, dissolvedCountyLines)
    arcpy.Buffer_analysis(inputCountyPolygons, bufferedCountyPolygons, "15500 Feet")
    
    bufferedCountyPolygonList = list()
    outputFeatureList = list()
    
    # 1st SearchCursor
    newCursor = daSearchCursor(bufferedCountyPolygons, bufferCursorFields)
    for newRow in newCursor:
        bufferedCountyPolygonList.append(list(newRow))
        
    if 'newCursor' in locals():
        del newCursor
    else:
        pass
    
    arcpy.MakeFeatureLayer_management(bufferedCountyPolygons, loadedCounties)
    
    for listedRow in bufferedCountyPolygonList:
        selectNumber = listedRow[0]
        
        whereClause = " \"OBJECTID\" = '" + str(selectNumber)  + "' "
        arcpy.SelectLayerByAttribute_management(loadedCounties, "NEW_SELECTION", whereClause)
        
        arcpy.Intersect_analysis([dissolvedCountyLines, loadedCounties], tempCountyLines, "ALL")
        
        # 2nd SearchCursor
        newCursor = daSearchCursor(tempCountyLines, ["SHAPE@", "County_Number", "County_Name"])
        for newRow in newCursor:
            outputFeatureList.append(newRow)
        
        if 'newCursor' in locals():
            del newCursor
        else:
            pass
    
    
    # 1st CreateFeatures_management
    # 1st, 2nd AddField_management
    lambertProjectionLocationKansas = r"\\gisdata\ArcGIS\GISdata\NAD_83_Kansas_Lambert_Conformal_Conic_Feet.prj"
    arcpy.CreateFeatureclass_management(r'Database Connections\countyMapsSQLSDE.sde', "CountyLinesIntersected", "POLYLINE", "", "", "", lambertProjectionLocationKansas)
    
    arcpy.AddField_management(outputCountyLines, "County_Number", "DOUBLE", "", "", "")
    
    arcpy.AddField_management(outputCountyLines, "County_Name", "TEXT", "", "", "55")
    
    print "First Intersected County Row: " + str(outputFeatureList[0])
    
    # 1st InsertCursor
    # Use this again later. Very useful. -- Will need when trying to deserialize arcpy objects from multiprocessing and
    # then write them to a feature class, since I'll have to call arcpy.point(array) where array is an x,y coord in a
    # list format prior to writing them to a gdb or sde.
    newCursor = daInsertCursor(os.path.join(r'Database Connections\countyMapsSQLSDE.sde', 'CountyLinesIntersected'), ["SHAPE@", "County_Number", "County_Name"])
    counter = 1
    for outputFeature in outputFeatureList:
        rowToInsert = ([outputFeature])
        
        insertedOID = newCursor.insertRow(outputFeature)
        
        counter += 1
        
        print "Inserted Row with Object ID of " + str(insertedOID)
        
    if 'newCursor' in locals():
        del newCursor
    else:
        pass


if __name__ == '__main__':
    #ImportAllSheets(excelSettingsLocation, gdbLocation)
    #nonStateAndCountyImport()
    countyAndRoadPreprocessing()
    countyBuffersAndNon_StateErase()
    #countyOnlyBridgeExport()
    #createCountyLinesForEachCounty()
    
else:
    pass

# Next script: countymaproadnamebordercreation.py