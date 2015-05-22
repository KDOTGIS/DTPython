#!/usr/bin/env python
# -*- coding: utf-8 -*-
# CountyMapRoadNameBorderCreationMulti.py

## Even though this has the name *multi.py it is not yet set
## up for multiprocessing. Have been working on bug fixes,
## added functionality, and moving the single process version
## to the SQL database instead.


##############################################################################
##############################################################################
##############################################################################
# Need to change this to use multiprocessing:
# 1) Work on a county-by-county basis.
# 2) Aggregate all of the data back together
#     into a combined points file at the end.
# 3) Don't create temp files. Instead, just add to a list
#     in the main process.
#     The main process list will then be written to a layer in an fgdb.
# 4) queue.put(listoflists) should work to add a list of all the lists
#     processed by the subprocess as points, with the geometries
#     as x, y instead of the actual point geometry.
#     should be able to use pointname.X and pointname.Y
#     to access the geometries and write them
#     as a tuple into the list.
#     [[(point.X, point.Y), "Wisconsin Rd", 1, "Allen"]
#     [(point2.X, point2.Y), "New Hampshire Rd", 1, "Allen"]]
#     ^Example of a multilist-list with point location as the first
#     variable, in tuple form.
# 5) Converting the data to a point and writing it to a geodatabase
#     should be fairly straightforward from there
#     using the SHAPE token and arcpy.point(pointtuple).
# 6) Getting the data into the processes may be more difficult,
#     however, as each process will need to load a polygon geometry
#     and several line geometries.
#     This might be solveable with search cursors. Use a where clause if
#     possible, to speed it up.
##############################################################################
##############################################################################
##############################################################################

# Need to work on adding multiprocessing to this
# and then remove duplicates within
# a spatial distance.


# pointDeleteList = list()
# for eachPoint:
#     pointObjectID = eachPoint[0]
#     for otherPoint:
#         if otherPoint[0] != pointObjectID:
#            if(testForSameName() == True):
#                testForAndDeleteIfTooClose

## Might be faster/simpler to start with the
## name test.
## If two points share the same name AND same county,
## or a caps/uncaps name AND county that would be
## the same if they had the same capitalization
## then test them for close distance.

## If they are close to one another, delete
## the one(s) with the higher objectID.

## Can probably create a selection list
## that can be applied all together
## or broken into smaller lists if need be
## then deleted all at once or
## in smaller sections.

## Really shouldn't be that many duplicate
## points to delete, however. One list
## should still be small enough to be
## selected and deleted all in
## one sequence.


gdb = r'\\gisdata\ArcGIS\GISdata\GDB\CountyMappingData.gdb'
sdeConn = r'Database Connections\countyMapsSQLSDE.sde'

from arcpy import env
from arcpy.da import InsertCursor as daInsertCursor, UpdateCursor as daUpdateCursor, SearchCursor as daSearchCursor, Editor as daEditor  # @UnresolvedImport @UnusedImport
import arcpy
import math
from math import radians, sin, cos, floor, sqrt  # @UnusedImport
import os

env.workspace = gdb
env.overwriteOutput = True
env.outputZFlag = "Disabled"

countyBorderFeature = os.path.join(gdb, 'Counties_No_Z_Extension_Buffer')
countyRoadsFeature = os.path.join(gdb, 'Non_State_System_For_Point_Creation')
countyRoadsFeaturePrereduction = os.path.join(gdb, 'Non_State_System_Prereduction')
countyRoadsBorderFeature = os.path.join(gdb, 'TempIntersectedRoadsBorder')
createdExtensionLines = os.path.join(gdb, "createdExtensionLines")
countyRoadNameRosette = os.path.join(gdb, "countyRoadNameRosette")
tempRoadNameRosette = os.path.join(gdb, "tempRoadNameRosette")
tempRoadNameRosetteSinglePoint = os.path.join(gdb, "tempRoadNameRosetteSinglePoint")
pointsToSplitBy = os.path.join(gdb, "pointsToSplitBy")
endPointsFC = os.path.join(gdb, "endPointsSinglePart")

roadCursorFields = ["OBJECTID", "OID@", "SHAPE@", "RD_NAMES", "COUNTY_NUMBER"]
countyBorderFields = ["OBJECTID", "SHAPE@XY", "SQRT_DIV8", "COUNTY_NAME", "COUNTY_NUMBER"]
countyRoadNameRosetteFields = ["LabelAngle", "COUNTY_NAME", "COUNTY_NUMBER"]

# Get/use the same projection as the one used for the county roads.
spatialReferenceProjection = arcpy.Describe(countyRoadsFeature).spatialReference

#lambertProjectionLocationKansas = r"\\gisdata\ArcGIS\GISdata\NAD_83_Kansas_Lambert_Conformal_Conic_Feet.prj"


def getBorderFeatureList():
    print "Getting border feature list."
    
    borderFeatureCursor = daSearchCursor(countyBorderFeature, countyBorderFields)
    
    borderFeaturesToReturn = list()
    
    for borderFeature in borderFeatureCursor:
        borderFeaturesToReturn.append(borderFeature)
        
    # Just return the borderFeature... have other operations get the countyBorderFeatureCentroid
    # and countyBorderFeatureArea as needed.
    
    return borderFeaturesToReturn


def calcPointDistance(point1, point2):
    
    point2X = point2[0]
    point1X = point1[0]
    
    point2Y = point2[1]
    point1Y = point1[1]
    
    distanceBetweenPoints = math.sqrt(((point2X - point1X)*(point2X - point1X))+((point2Y - point1Y)*(point2Y - point1Y)))
    
    return distanceBetweenPoints


def getRoadLinesList():
    
    print "Getting the road lines list."
    # Need a new function here. -- Instead of calling this twice, have a main-style funtion
    # call it once and then pass it as an argument to both functions.
    roadCursor = daSearchCursor(countyRoadsFeature, roadCursorFields)  # @UndefinedVariable
    
    roadLinesToReturn = list()
    
    for roadPolyline in roadCursor:
        roadLinesToReturn.append(list(roadPolyline))
        
    if "roadCursor" in locals():
        del roadCursor
    else:
        pass
    
    return roadLinesToReturn


'''
def getOriginalRoadEndPointsList():
    
    roadLinesList = getRoadLinesList()
    
    pointsList = list()
    
    originalRoadEndPointsToReturn = list()
    
    for roadPolyline in roadLinesList:
        
        totalLength = roadPolyline[2].length
        newPoint = roadPolyline[2].positionAlongLine(0)
        
        secondNewPoint = roadPolyline[2].positionAlongLine(totalLength)
        
        pointsList.append(newPoint)
        pointsList.append(secondNewPoint)
        
        tupleToAdd = (newPoint.firstPoint.X, newPoint.firstPoint.Y, roadPolyline[3])
        
        originalRoadEndPointsToReturn.append(tupleToAdd)
        
        tupleToAdd = (secondNewPoint.firstPoint.X, secondNewPoint.firstPoint.Y, roadPolyline[3])
        
        originalRoadEndPointsToReturn.append(tupleToAdd)
    
    if "roadLinesList" in locals():
        del roadLinesList
    else:
        pass
    
    
    if arcpy.Exists("endPointsSinglePart"):
        arcpy.Delete_management("endPointsSinglePart")
    else:
        pass
    
    arcpy.CreateFeatureclass_management(gdb, "endPointsSinglePart", "POINT", "", "", "", spatialReferenceProjection)
    
    newEditingSession = daEditor(gdb)
    newEditingSession.startEditing()
    newEditingSession.startOperation()
    
    endPointsSinglePartCursor = arcpy.da.InsertCursor(endPointsFC, ["SHAPE@"])  # @UndefinedVariable
    
    for listedPoint in pointsList:
        pointToAdd = arcpy.Point(listedPoint.firstPoint.X, listedPoint.firstPoint.Y)
        
        endPointsSinglePartCursor.insertRow([pointToAdd])
    
    newEditingSession.stopOperation()
    newEditingSession.stopEditing(True)
    
    if "endPointsSinglePartCursor" in locals():
        del endPointsSinglePartCursor
    else:
        pass
    
    return originalRoadEndPointsToReturn
'''


def removeSmallRoads():
    
    print "Removing the small roads from the data."
    
    arcpy.CopyFeatures_management(countyRoadsFeature, countyRoadsFeaturePrereduction)
    
    inMemoryRoadsLayer = 'inMemoryRoadsLayerFC'
    
    arcpy.MakeFeatureLayer_management(countyRoadsFeature, inMemoryRoadsLayer)
    
    roadsReductionWhereClause = ' "SHAPE_Length" <= 1500 '
    
    arcpy.SelectLayerByAttribute_management(inMemoryRoadsLayer, "NEW_SELECTION", roadsReductionWhereClause)
    
    selectedRoadsCount = arcpy.GetCount_management(inMemoryRoadsLayer)
    
    if selectedRoadsCount >= 1:
        arcpy.DeleteFeatures_management(inMemoryRoadsLayer)
    else:
        pass


def extendAndIntersectRoadFeatures(): # Place the operations that extend each road line segment by a certain distance here.
    # Should extend all the features that exist in the post-erase dataset. Might be more difficult
    # to calculate the angle of these lines accurately, but it should be easier to figure out
    # than trying to get the lines to split correctly with the buggy SplitLineAtPoint tool.
    
    # Extend the lines in both directions by X_Val Feet.
    
    print "Starting to extend and intersect road features."

    if arcpy.Exists(createdExtensionLines):
        arcpy.Delete_management(createdExtensionLines)
    else:
        pass
    
    
    arcpy.CreateFeatureclass_management(gdb, "createdExtensionLines", "POLYLINE", "", "", "", spatialReferenceProjection)
    
    # Add a column for roadname called roadNameForSplit.
    arcpy.AddField_management(createdExtensionLines, "roadNameForSplit", "TEXT", "", "", "55")
    
    # Add a column which stores the angle to display a label called called LabelAngle.
    arcpy.AddField_management(createdExtensionLines, "LabelAngle", "DOUBLE", "", "", "") # Change to double.
    
    # Add a column which stores the County Number.
    arcpy.AddField_management(createdExtensionLines, "County_Number", "DOUBLE", "", "", "")
    
    # Hard coded the buffer distance to 22176 instead of calculating based on SQRT_DIV8 field value.
    extensionDistance = 22176 # (4.2 * 5280)
    
    roadLinesToInsertList = list()
    
    roadLinesList = getRoadLinesList()
    
    for roadLinesItem in roadLinesList:
        
        roadNameToUse = roadLinesItem[3]
        countyNumber = roadLinesItem[4]
        
        linePointsArray = arcpy.Array()
        
        firstPointTuple = (roadLinesItem[2].firstPoint.X, roadLinesItem[2].firstPoint.Y)
        lastPointTuple = (roadLinesItem[2].lastPoint.X, roadLinesItem[2].lastPoint.Y)
        
        
        # Make this a two-step process.
        # Might... maybe, possibly, be as simple as
        # adding _1 to the end of the first set of variables,
        # adding _2 to the end of the second set of variables,
        # then making the extensions in both directions
        # and creating a new line that has the endpoints
        # from both sides as it's first and last point.
        # if necessary, could add the other points in between
        # but probably not necessary just for generating
        # an intersection point.
        
        
        yValue_1 = -(lastPointTuple[1] - firstPointTuple[1]) # made y value negative
        xValue_1 = lastPointTuple[0] - firstPointTuple[0]
        
        lineDirectionAngle_1 = math.degrees(math.atan2(xValue_1, yValue_1)) # reversed x and y
        
        lineDirectionAngle_1 = -(((lineDirectionAngle_1 + 180) % 360) - 180) # correction for certain quadrants
        #print "lineDirectionAngle: " + str(lineDirectionAngle_1)
        
        origin_x_1 = firstPointTuple[0]
        origin_y_1 = firstPointTuple[1]
        
        
        yValue_2 = -(firstPointTuple[1] - lastPointTuple[1]) # made y value negative
        xValue_2 = firstPointTuple[0] - lastPointTuple[0]
        
        lineDirectionAngle_2 = math.degrees(math.atan2(xValue_2, yValue_2)) # reversed x and y
        
        lineDirectionAngle_2 = -(((lineDirectionAngle_2 + 180) % 360) - 180) # correction for certain quadrants
        #print "lineDirectionAngle: " + str(lineDirectionAngle_2)
        
        origin_x_2 = lastPointTuple[0]
        origin_y_2 = lastPointTuple[1]
        
        (disp_x_1, disp_y_1) = (extensionDistance * math.sin(math.radians(lineDirectionAngle_1)),
                          extensionDistance * math.cos(math.radians(lineDirectionAngle_1)))
        
        (end_x_1, end_y_1) = (origin_x_1 + disp_x_1, origin_y_1 + disp_y_1)
        
        
        (disp_x_2, disp_y_2) = (extensionDistance * math.sin(math.radians(lineDirectionAngle_2)),
                          extensionDistance * math.cos(math.radians(lineDirectionAngle_2)))
        
        (end_x_2, end_y_2) = (origin_x_2 + disp_x_2, origin_y_2 + disp_y_2)
        
        startPoint = arcpy.Point()
        endPoint = arcpy.Point()
        
        startPoint.ID = 0
        startPoint.X = end_x_1
        startPoint.Y = end_y_1
        
        endPoint.ID = 1
        endPoint.X = end_x_2
        endPoint.Y = end_y_2
        
        linePointsArray.add(startPoint)
        linePointsArray.add(endPoint)
        
        newLineFeature = arcpy.Polyline(linePointsArray)
        
        # Need to create an extension for both ends of the line and add them
        # to the array.
        
        #newLineFeature = createdExtensionLinesCursor.newRow()
        
        #newLineFeature.SHAPE = linePointsArray
        
        lineDirectionOutput = "0"
        
        if lineDirectionAngle_1 > 0:
            lineDirectionOutput = lineDirectionAngle_1
        elif lineDirectionAngle_2 > 0:
            lineDirectionOutput = lineDirectionAngle_2
        else:
            pass
        
        
        roadLinesToInsertList.append([newLineFeature, roadNameToUse, lineDirectionOutput, countyNumber])
        
        #createdExtensionLinesCursor.insertRow([newLineFeature, roadNameToUse, lineDirectionOutput])
        
        if "newLineFeature" in locals():
            del newLineFeature
        else:
            pass
    
    # Consider building this as a separate list and then just looping
    # through the list to put it into the cursor instead
    # of doing logic and inserting into the cursor at the same place.
    
    
    #start editing session
    newEditingSession = daEditor(gdb)
    newEditingSession.startEditing()
    newEditingSession.startOperation()
    
    createdExtensionLinesCursor = daInsertCursor(createdExtensionLines, ["SHAPE@", "roadNameForSplit", "LabelAngle", "County_Number"])
    
    for roadLinesToInsertItem in roadLinesToInsertList:
        createdExtensionLinesCursor.insertRow(roadLinesToInsertItem)
    
    
    # End editing session
    newEditingSession.stopOperation()
    newEditingSession.stopEditing(True)
    
    if "createdExtensionLinesCursor" in locals():
        del createdExtensionLinesCursor
    else:
        pass
    
    if arcpy.Exists("countyRoadNameRosette"):
        arcpy.Delete_management("countyRoadNameRosette")
    else:
        pass
    
    arcpy.CreateFeatureclass_management(gdb, "countyRoadNameRosette", "POINT", "", "", "", spatialReferenceProjection)
    
    arcpy.AddField_management(countyRoadNameRosette, "roadNameForSplit", "TEXT", "", "", "55")
    
    arcpy.AddField_management(countyRoadNameRosette, "LabelAngle", "DOUBLE", "", "", "") # Change to double.
    
    arcpy.AddField_management(countyRoadNameRosette, "County_Number", "DOUBLE", "", "", "")
    
    arcpy.AddField_management(countyRoadNameRosette, "COUNTY_NAME", "TEXT", "", "", "55")
    
    
    # Now then, need to check for the existence
    # of and delete the point intersection layer
    # if it exists.
    
    # Then, recreate it and the proper fields.
    
    inMemoryCountyBorderExtension = "aCountyBorderExtensionBuffer"
    inMemoryExtensionLines = "aLoadedExtensionLines"
    
    # Temporary layer, use CopyFeatures_management to persist to disk.
    arcpy.MakeFeatureLayer_management(countyBorderFeature, inMemoryCountyBorderExtension) # County Border extension feature
    
    # Temporary layer, use CopyFeatures_management to persist to disk.
    arcpy.MakeFeatureLayer_management(createdExtensionLines, inMemoryExtensionLines) # Line extension feature
    
    borderFeatureList = getBorderFeatureList()
    
    borderFeatureList = sorted(borderFeatureList, key=lambda feature: feature[4])
    
    for borderFeature in borderFeatureList:
        borderFeatureName = borderFeature[3]
        borderFeatureNumber = borderFeature[4]
        print "borderFeatureName: " + str(borderFeatureName) + " & borderFeatureNumber: " + str(int(borderFeatureNumber))
        
        
        countyBorderWhereClause = ' "COUNTY_NUMBER" = ' + str(int(borderFeatureNumber)) + ' '
        
        arcpy.SelectLayerByAttribute_management(inMemoryCountyBorderExtension, "NEW_SELECTION", countyBorderWhereClause)
        
        
        countyBorderSelectionCount = arcpy.GetCount_management(inMemoryCountyBorderExtension)
        
        print "County Borders Selected: " + str(countyBorderSelectionCount)
        
        
        # Had to single-quote the borderFeatureNumber because it is stored as a string in the table.
        # Unsingle quoted because it was changed to a float.
        extensionLinesWhereClause = ' "COUNTY_NUMBER" = ' + str(int(borderFeatureNumber)) + ' '
        
        arcpy.SelectLayerByAttribute_management(inMemoryExtensionLines, "NEW_SELECTION", extensionLinesWhereClause)
        
        
        extensionLineSelectionCount = arcpy.GetCount_management(inMemoryExtensionLines)
        
        print "Extension Lines Selected: " + str(extensionLineSelectionCount)
        
        if arcpy.Exists("tempRoadNameRosette"):
            arcpy.Delete_management("tempRoadNameRosette")
        else:
            pass
        
        if arcpy.Exists("tempRoadNameRosetteSinglePoint"):
            arcpy.Delete_management("tempRoadNameRosetteSinglePoint")
        else:
            pass
        
        arcpy.Intersect_analysis([inMemoryCountyBorderExtension, inMemoryExtensionLines], tempRoadNameRosette, "ALL", "", "POINT")
        
        # Intersect to an output temp layer.
        
        # Next, need to loop through all of the counties.
        
        # Get the county number and use it to select
        # a county extension buffer in the county
        # extension buffers layer.
        
        # Then, use the county number to select
        # all of the lines for that county
        # in the extension lines layer.
        
        # Then, export those to a temp layer in the fgdb.
        
        # Change multipoint to singlepoint.
        
        # Was working until I moved from gisprod to sdedev for the data source.
        # not sure why. Check to make sure projections match.
        
        try:
            
            # Run the tool to create a new fc with only singlepart features
            arcpy.MultipartToSinglepart_management(tempRoadNameRosette, tempRoadNameRosetteSinglePoint)
            
            # Check if there is a different number of features in the output
            #   than there was in the input
            inCount = int(arcpy.GetCount_management(tempRoadNameRosette).getOutput(0))
            outCount = int(arcpy.GetCount_management(tempRoadNameRosetteSinglePoint).getOutput(0))
             
            if inCount != outCount:
                print "Found " + str(outCount - inCount) + " multipart features."
                #print "inCount, including multipart = " + str(inCount)
                #print "outCount, singlepart only = " + str(outCount)
                
            else:
                print "No multipart features were found"
        
        except arcpy.ExecuteError:
            print arcpy.GetMessages()
        except Exception as e:
            print e
        
        print "Appending the temp point layer to the county point intersection layer."
        
        arcpy.Append_management([tempRoadNameRosetteSinglePoint], countyRoadNameRosette, "NO_TEST")
        
        # K, worked once. Just need to change LabelAngle to a float and it might be what
        # I want... except for too slow, but that's why we have the multiprocessing module.
        # So add multiprocessing capability after it correctly creates the desired output.
        # Will need to change the way the temp files are handled/named, but should be
        # fairly simple. -- Getting the multiprocessing module to work might be less
        # simple, but still probably worth it for the speed increase.
        
        # For multiprocessing: have each county receive a random number after its temp file,
        # i.e. try: write feature with random number, except retry with different number.
        # then, read all of the temp file
        
        # Then, print a completion message
        # and check the points out in a map.
        
        print "Done adding points to the countyRoadNameRosette feature class."
        
    print "Normalizing the label angle values."
    
    ## Might need to add another field to this feature class for the offset on
    ## labels, then calculate it based off of the SQRT_DIV8 field.
    
    # Points are currently in lambert conformal conic. Probably shouldn't be. Not showing up properly
    # on the county maps. Make sure to get the data from SDEPROD or SDEDEV.
    
    # Might also need to check for and erase points that have a label angle which
    # is more than 20 degrees off from 0, 90, 180, 270, as these are likely to
    # be minor roads.
    
    # Reorganize to be more than one function instead of being a ~300 line long function.
    
    
def labelAngleNormalization():
    
    if "COUNTY_NAME" not in arcpy.ListFields(countyRoadNameRosette):
        arcpy.AddField_management(countyRoadNameRosette, "COUNTY_NAME", "TEXT", "", "", "55")
    else:
        pass
    
    newCursor = daSearchCursor(countyBorderFeature, countyBorderFields)
    
    countyTranslationDictionary = dict()
    
    for countyBorderItem in newCursor:
        if countyBorderItem[4] not in countyTranslationDictionary:
            countyTranslationDictionary[countyBorderItem[4]] = countyBorderItem[3]
        else:
            pass
    
    if "newCursor" in locals():
        del newCursor
    else:
        pass
    
    
    newCursor = daUpdateCursor(countyRoadNameRosette, countyRoadNameRosetteFields)
    
    for countyPointItem in newCursor:
        countyPointItem = list(countyPointItem)
        
        # Takes the remainder of the angle divided by 360.
        countyPointItem[0] = math.fmod(countyPointItem[0], 360) # Uses fmod due to floating point issues with the modulo operator in python.
        
        if countyPointItem[0] >= 250 and countyPointItem[0] <= 290:
            countyPointItem[0] = 270
            if countyPointItem[2] in countyTranslationDictionary:
                countyPointItem[1] = countyTranslationDictionary[countyPointItem[2]]
            else:
                countyPointItem[1] = ""
            newCursor.updateRow(countyPointItem)
            
        elif countyPointItem[0] >= 160 and countyPointItem[0] <= 200:
            countyPointItem[0] = 180
            if countyPointItem[2] in countyTranslationDictionary:
                countyPointItem[1] = countyTranslationDictionary[countyPointItem[2]]
            else:
                countyPointItem[1] = ""
            newCursor.updateRow(countyPointItem)
            
        elif countyPointItem[0] >= 70 and countyPointItem[0] <= 110:
            countyPointItem[0] = 90
            if countyPointItem[2] in countyTranslationDictionary:
                countyPointItem[1] = countyTranslationDictionary[countyPointItem[2]]
            else:
                countyPointItem[1] = ""
            newCursor.updateRow(countyPointItem)
            
        elif (countyPointItem[0] >= 0 and countyPointItem[0] <= 20) or (countyPointItem[0] >= 340 and countyPointItem[0] <= 360):
            countyPointItem[0] = 0
            if countyPointItem[2] in countyTranslationDictionary:
                countyPointItem[1] = countyTranslationDictionary[countyPointItem[2]]
            else:
                countyPointItem[1] = ""
            newCursor.updateRow(countyPointItem)
            
        else:
            print "Deleting row for having an angle more than 20 degrees away from a cardinal direction."
            newCursor.deleteRow()
            
         
    if "newCursor" in locals():
        del newCursor
    else:
        pass
    
    
    print "Label angle normalization complete!"
    print "Done extending and intersecting road features." # Need to break this into two pieces and pass some of the inmemorylayers
    # from the first function to the 2nd or similar.
    # the function is just too long to be easily readable/debuggable.


def transferDataToSQLServer():
    if arcpy.Exists(countyRoadNameRosette):
        print "Data exists. Transferring to SQL Server."
        try:
            arcpy.CopyFeatures_management (countyRoadNameRosette, os.path.join(sdeConn, "countyRoadNameRosette"))
            print "Transfer completed successfully."
        except:
            print "An error occurred during the transfer."
    else:
        print "Data does not exist. Nothing to transfer to SQL Server."
        
# Define a new function to delete out the bridges that show up inside city boundaries.
# The non-state system already has bridges removed, I think.


if __name__ == "__main__":
    #removeSmallRoads()
    #extendAndIntersectRoadFeatures()
    #labelAngleNormalization()
    #thresholdRemoval()
    transferDataToSQLServer()
    pass

else:
    pass


## Next script: countymapdatadrivenpagestopdfmulti.py