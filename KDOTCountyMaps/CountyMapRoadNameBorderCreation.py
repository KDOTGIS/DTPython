#!/usr/bin/env python
# -*- coding: utf-8 -*-
# CountyMapRoadNameBorderCreation.py


##############################################################################
##############################################################################
##############################################################################
# To reconfigure this to use multiprocessing...
# Need to regrok what's going on here and change it to:
# 1) Work with the new data.
# 2) Work on a county-by-county basis.
# 3) Aggregate all of the data back together
#     into a combined points file at the end.
# 4) Clean up the temp files created along
#     the way.
# 4a) Look at using the aggregation style
#     employed in the createCountyLinesForEachCounty() function
#     in the CountyMapPreprocessing script.
##############################################################################
##############################################################################
##############################################################################


# When finished, work on the script logging function and then add it into this script.
# Also, move this script to a server and schedule it to run once a month or so.


gdbLocation = r'Database Connections\countyMapsSQLSDE.sde'
gdbPlusUserSchema = gdbLocation + '\countyMaps.SDE.'

from arcpy import env
from arcpy.da import InsertCursor as daInsertCursor, UpdateCursor as daUpdateCursor, SearchCursor as daSearchCursor, Editor as daEditor  # @UnresolvedImport @UnusedImport
import arcpy
import math
from math import radians, sin, cos, floor, sqrt, pow  # @UnusedImport
import os
import datetime

env.workspace = gdbLocation
env.overwriteOutput = True
env.outputZFlag = "Disabled"

countyBorderFeature = gdbPlusUserSchema + 'Counties_No_Z_Extension_Buffer'
countyRoadsFeature = gdbPlusUserSchema + 'Non_State_System_For_Point_Creation'
countyRoadsFeaturePrereduction = gdbPlusUserSchema + 'Non_State_System_Prereduction'
countyRoadsBorderFeature = gdbPlusUserSchema + 'TempIntersectedRoadsBorder'
createdExtensionLines = gdbPlusUserSchema + "createdExtensionLines"
countyRoadNameRosette = gdbPlusUserSchema + "countyRoadNameRosette"
tempRoadNameRosette = gdbPlusUserSchema + "tempRoadNameRosette"
tempRoadNameRosetteSinglePoint = gdbPlusUserSchema + "tempRoadNameRosetteSinglePoint"
pointsToSplitBy = gdbPlusUserSchema + "pointsToSplitBy"
endPointsFC = gdbPlusUserSchema + "endPointsSinglePart"

roadCursorFields = ["OBJECTID", "OID@", "SHAPE@", "RD_NAMES", "COUNTY_NUMBER"]
#countyBorderFields = ["OBJECTID", "SHAPE@XY", "SQRT_DIV8", "COUNTY_NAME", "COUNTY_NUMBER"]
countyBorderFields = ["OBJECTID", "SHAPE@XY", "COUNTY_NAME", "COUNTY_NUMBER"]
countyRoadNameRosetteFields = ["LabelAngle", "COUNTY_NAME", "COUNTY_NUMBER"]
countyRoadNameRosetteFieldsObjShape = ["ObjectID", "SHAPE@XY", "roadNameForSplit", "COUNTY_NUMBER"]

# Get/use the same projection as the one used for the county roads.
spatialReferenceProjection = arcpy.Describe(countyRoadsFeature).spatialReference

#lambertProjectionLocationKansas = r"\\gisdata\ArcGIS\GISdata\NAD_83_Kansas_Lambert_Conformal_Conic_Feet.prj"


def FindDuration(endTime, startTime):
    #Takes two datetime.datetime objects, subtracting the 2nd from the first
    #to find the duration between the two.
    duration = endTime - startTime
    
    dSeconds = int(duration.seconds)
    durationp1 = str(int(dSeconds // 3600)).zfill(2)
    durationp2 = str(int((dSeconds % 3600) // 60)).zfill(2)
    durationp3 = str(int(dSeconds % 60)).zfill(2)
    durationString = durationp1 + ':' +  durationp2 + ':' + durationp3
    
    return durationString


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
    
    xDifference = point2X - point1X
    yDifference = point2Y - point1Y
    
    distanceBetweenPoints = math.sqrt( xDifference * xDifference + yDifference * yDifference )
    
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


def removeSmallRoads():
    
    print "Removing the small roads from the data."
    
    arcpy.CopyFeatures_management(countyRoadsFeature, countyRoadsFeaturePrereduction)
    
    inMemoryRoadsLayer = 'inMemoryRoadsLayerFC'
    
    arcpy.MakeFeatureLayer_management(countyRoadsFeature, inMemoryRoadsLayer)
    
    roadsReductionWhereClause = ' Shape.STLength() <= 1500 '
    
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
    
    
    arcpy.CreateFeatureclass_management(gdbLocation, "createdExtensionLines", "POLYLINE", "", "", "", spatialReferenceProjection)
    
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
    #newEditingSession = daEditor(gdbLocation)
    #newEditingSession.startEditing()
    #newEditingSession.startOperation()
    
    createdExtensionLinesCursor = daInsertCursor(createdExtensionLines, ["SHAPE@", "roadNameForSplit", "LabelAngle", "County_Number"])
    
    for roadLinesToInsertItem in roadLinesToInsertList:
        createdExtensionLinesCursor.insertRow(roadLinesToInsertItem)
    
    
    # End editing session
    #newEditingSession.stopOperation()
    #newEditingSession.stopEditing(True)
    
    if "createdExtensionLinesCursor" in locals():
        del createdExtensionLinesCursor
    else:
        pass
    
    # Remove the previous countyRoadNameRosette so that it can be recreated.
    if arcpy.Exists("countyRoadNameRosette"):
        arcpy.Delete_management("countyRoadNameRosette")
    else:
        pass
    
    arcpy.CreateFeatureclass_management(gdbLocation, "countyRoadNameRosette", "POINT", "", "", "", spatialReferenceProjection)
    
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
    
    borderFeatureList = sorted(borderFeatureList, key=lambda feature: feature[3])
    
    for borderFeature in borderFeatureList:
        borderFeatureName = borderFeature[2]
        borderFeatureNumber = borderFeature[3]
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
        
    #print "Normalizing the label angle values."
    
    ## Might need to add another field to this feature class for the offset on
    ## labels, then calculate it based off of the SQRT_DIV8 field.
    
    # Points are currently in lambert conformal conic. Probably shouldn't be. Not showing up properly
    # on the county maps. Make sure to get the data from SDEPROD or SDEDEV.
    
    # Might also need to check for and erase points that have a label angle which
    # is more than 20 degrees off from 0, 90, 180, 270, as these are likely to
    # be minor roads.
    
    # Reorganize to be more than one function instead of being a ~300 line long function.


def labelAngleNormalization():
    
    print "Normalizing the label angle values."
    
    if "COUNTY_NAME" not in arcpy.ListFields(countyRoadNameRosette):
        arcpy.AddField_management(countyRoadNameRosette, "COUNTY_NAME", "TEXT", "", "", "55")
    else:
        pass
    
    newCursor = daSearchCursor(countyBorderFeature, countyBorderFields)
    
    countyTranslationDictionary = dict()
    
    # countyBorderItem[3] is the number, countyBorderItem[2] is the name.
    # -- Use for translating from county number to county name.
    for countyBorderItem in newCursor:
        if countyBorderItem[3] not in countyTranslationDictionary: 
            countyTranslationDictionary[countyBorderItem[3]] = countyBorderItem[2]
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
        
        # countyPointItem[1] is County Name, countyPointItem[2] is County Number.
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


def thresholdRemoval():
    # Change to look at the number of roads that are in the
    # county's erased polygon.
    # Then, if there are not at least 60% of that many
    # roads labeled as points in the pointIntersection
    # layer, remove ALL points for that county.
    
    thresholdValue = 25 # 1 through 100, percentage as integer. ## 25 seems to work well. Results in only 10 counties not having enough points.
    # One county (42) doesn't have enough roads information for this script to do anything.
    
    #makefeaturelayer1
    arcpy.MakeFeatureLayer_management(countyRoadsFeature, "loadedCountyRoads")
    #makefeaturelayer2
    arcpy.MakeFeatureLayer_management(countyRoadNameRosette, "loadedRoadNameRosette")
    
    for i in xrange(1, 106):
        thresholdWhereClause = " \"COUNTY_NUMBER\" = " + str(i) + " "
        
        #selectfeatures1
        arcpy.SelectLayerByAttribute_management("loadedCountyRoads", "NEW_SELECTION", thresholdWhereClause)
        #selectfeatures2
        arcpy.SelectLayerByAttribute_management("loadedRoadNameRosette", "NEW_SELECTION", thresholdWhereClause)
        
        #createfeaturelayer with whereclause, or do this then make a select clause.
        countyRoadsCount = arcpy.GetCount_management("loadedCountyRoads")
        countyPointsCount = arcpy.GetCount_management("loadedRoadNameRosette")
        
        countyRoadsCount = int(countyRoadsCount.getOutput(0))
        countyPointsCount = int(countyPointsCount.getOutput(0))
        
        if countyRoadsCount >= 1:
            if (float(countyPointsCount) / float(countyRoadsCount)) >= (float(thresholdValue) / float(100)) and countyPointsCount >= 20:
                print "Threshold value OK for County Number: " + str(i) + "."
                pass
            else:
                print "Threshold value not met for County Number: " + str(i) + "."
                if countyPointsCount >= 1:
                    print "Removing road name rosette points from this county."
                    arcpy.DeleteRows_management("loadedRoadNameRosette")
                else:
                    print "Would have deleted the points for this county, but none exist to delete."
        else:
            print "No County Roads found for County Number: " + str(i) + "."
            
            
def duplicateNameRemoval():
    print "Starting duplicate name removal."
    newCursor = daSearchCursor(countyRoadNameRosette, countyRoadNameRosetteFieldsObjShape)
    
    countyNamePointList = list()
    
    for eachPoint in newCursor:
        countyNamePointList.append(eachPoint)
        
    if "newCursor" in locals():
        del newCursor
    else:
        pass
    
    pointDeleteList = list()
    
    for pointItem in countyNamePointList:
        for pointToCheck in countyNamePointList:
            # If the points share a road name, and a county number, but not the same ObjectID...
            if pointItem[0] not in pointDeleteList:
                if pointItem[3] == pointToCheck[3] and str(pointItem[2]).upper() == str(pointToCheck[2]).upper() and (not pointItem[0] == pointToCheck[0]):
                    # Use the distance formula to check to see if these points are within a
                    # certain distance from one another.
                    # If so, add the pointToCheck to the pointDeleteList.
                    distance = 0
                    point1 = pointItem[1]
                    point2 = pointToCheck[1]
                    
                    
                    distance = calcPointDistance(point1, point2)
                    
                    # Added "and pointToCheck not in pointDeleteList"
                    # to prevent two points from both adding a 3rd point to the list.
                    # Also, the distance looks enormous, but it's only about 1500 meters in Lambert_Conformal_Conic_2SP.
                    # @ 450,000 = maxDistance. -- Check smaller values before implementing, however...
                    # as going from 15000 to 450000 adds a long time to this function's execution.
                    # maybe remove the equality on the upper bound, and change the lower bound
                    # to -1 or something like that.
                    
                    # Change this to add just the objectid to the pointDeleteList
                    # instead of the whole point row to increase the speed
                    # of the check when the list grows to a decent size.
                    # Distance of 10000 seems to give good results.
                    if distance >= 0 and distance < 10000 and pointToCheck[0] not in pointDeleteList:
                        pointDeleteList.append(pointToCheck[0])
                    else:
                        pass
                else:
                    pass
            else:
                pass
    
    newCursor = daUpdateCursor(countyRoadNameRosette, countyRoadNameRosetteFieldsObjShape)
    
    for updateableRow in newCursor:
        for pointToDeleteOID in pointDeleteList:
            if updateableRow[0] == pointToDeleteOID:
                print "Selected a point for " + str(updateableRow[2]) + " in " + str(updateableRow[3]) + " county to delete."
                newCursor.deleteRow()
                print "Point deleted."
            else:
                pass
        #updateCursor
        #delete pointToDelete from countyRoadNameRosette.
        #print a message saying that the point was deleted.
    
    if "newCursor" in locals():
        del newCursor
    else:
        pass
    
    
if __name__ == "__main__":
    startingTime = datetime.datetime.now()
    
    removeSmallRoads()
    extendAndIntersectRoadFeatures()
    labelAngleNormalization()
    thresholdRemoval()
    duplicateNameRemoval()
    
    endingTime = datetime.datetime.now()
    
    scriptDuration = FindDuration(endingTime, startingTime)
    
    print "\n" # Newline for better readability.
    print "For the main/complete script portion..."
    print "Starting Time: " + str(startingTime)
    print "Ending Time: " + str(endingTime)
    print "Elapsed Time: " + scriptDuration
    
else:
    pass


## Next script: CountyMapDataDrivenPagesToPDF.py