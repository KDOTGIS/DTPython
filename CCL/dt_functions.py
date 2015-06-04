'''
Created on 2014-09-02
@author: dtalley
Updated 2015-06-04 by dtalley
'''

# Original version location: D:\KDOT_Python\KDOT_Imports
# Updated via locally cloned version.

# Import data paths from config file.  If testing in ArcMap, run config first to set up environments
# Rewrite to get this information from a different source than the CCL config file.
# Should not be importing things from cityconnectinglinktest.*
# This script should be imported into the cityconnectinglinktest scripts instead.


try:
    from cityconnectinglinktest.config import (ws, connection0, connection1, citylimits, stateroutelyr, cntyroutelyr, laneclass,  # @UnusedImport @UnresolvedImport
                        maintenance, resolve, LineFeatureClass, NewRouteKey, NewBeg, NewEnd, NewRoute,  # @UnusedImport @UnresolvedImport
                        schema)  # @UnusedImport @UnresolvedImport
except:
    print "Import from cityconnectinglinktest.config failed."
    pass

from arcpy import (da, env, AddField_management, ListFields, Intersect_analysis, LocateFeaturesAlongRoutes_lr,  
                    MakeFeatureLayer_management, MultipartToSinglepart_management, MakeRouteEventLayer_lr,  
                    CopyFeatures_management, SelectLayerByAttribute_management, GetCount_management, GetMessages)  

import sys
from math import ceil as mathCeil
import datetime
import cx_Oracle
env.workspace = ws
env.overwriteOutput = True
env.MResolution = 0.0001
env.MTolerance = 0.0002

scriptSuccess = '0x0'
scriptFailure = '0x1'

def ReportResolutionOrdering():
    # Create a list to hold the rows from the cursor.
    holderList = list()
    # Connection to the feature class
    fc = connection1+"CCL_Report"
    
    testForField = "RESOLUTION_ORDER"
    fieldSeen = 0
    
    # Look for the RESOLUTION_ORDER field in the table.
    fieldCheckList = ListFields(fc)
    for fieldCheckElement in fieldCheckList:
        if str.upper(str(fieldCheckElement.name)) == str.upper(testForField):
            fieldSeen += 1
            
    # If the RESOLUTION_ORDER field does not yet exist, add it.
    if fieldSeen == 0:
        print "Adding the Resolution_Order field to the CCL_Report table."
        AddField_management(connection1+"CCL_Report", "RESOLUTION_ORDER", "SHORT")
        print "Populating Resolution_Order with new values."
    else:
        print "The Resolution_Order field already exists within the CCL_Report table."
        print "Updating the Resolution_Order values."
        
    # Start the cursor to retrieve the rows from the feature class.
    #fieldList = list()
    fieldList = ['OBJECTID', 'CCL_LRS', 'CCL_BEGIN', 'DESCRIPTION', 'CITY', 'RESOLUTION_ORDER']
    # Cursor to read the all the fields and place them in an array.
    cursor = da.SearchCursor(fc, fieldList)  # @UndefinedVariable
    for row in cursor:
        listRow = list(row)
        holderList.append(listRow)
    
    if cursor:
        del cursor
    else:
        pass
    if row:
        del row
    else:
        pass
    
    # Create a dictionary to store the rows by City.
    rowListDictionary = {}
    
    # Loop through the list to build a dictionary with CCL_Routes as keys.
    for heldRow in holderList:
        # Each key will hold a list of lists.
        rowListContainer = list()
        # If the key already exists, assign the previous list of lists
        # to the list container, then append the new list
        # before updating the key in the dictionary.
        if heldRow[1] in rowListDictionary:
            rowListContainer = rowListDictionary[heldRow[1]]
            rowListContainer.append(heldRow)
            rowListDictionary[heldRow[1]] = rowListContainer
        # Otherwise, the key needs to be created
        # with the list container having only one list contained
        # within it for now.
        else:
            rowListContainer.append(heldRow)
            rowListDictionary[heldRow[1]] = rowListContainer
    
    for cclKey in rowListDictionary:
        outListContainer = rowListDictionary[cclKey]
        # Sort based on CCL_Begin.
        outListContainer.sort(key = lambda sortingRow: sortingRow[2])
        countVariable = 0
        descVariable = ''
        for outListIndex, outList in enumerate(outListContainer):
            
            # Is this the first list/row in the key's list container?
            # If so, then set the Resolution_Order to 0
            if outListIndex == 0:
                outList[5] = 0
                descVariable = outList[3]
            else:
                currentDesc = outList[3]
                # Check to see if the previous description is the same
                # as the current description.
                if currentDesc == descVariable:
                    # If so, set the Resolution_Order to
                    # the current countVariable
                    # and do not increment it.
                    outList[5] = countVariable
                else:
                    # The current desc is different than
                    # the previous desc, so update
                    # the count variable prior
                    # to assignment.
                    countVariable += 1
                    outList[5] = countVariable
                    descVariable = outList[3]
            
            outListContainer[outListIndex] = outList
            
        rowListDictionary[cclKey] = outListContainer
        
    # Need to add an update cursor that will update
    # the RESOLUTION_ORDER field with
    # values from the rowListDictionary
    # based on the shared OBJECTID field.
    
    fieldList = list()
    fieldList = ['OBJECTID', 'CCL_LRS', 'RESOLUTION_ORDER']
    
    cursor = da.UpdateCursor(fc, fieldList)  # @UndefinedVariable
    for row in cursor:
        cclKey = row[1]
        outListContainer = rowListDictionary[cclKey]
        for outList in outListContainer:
        #print "City: " + str(outList[4]) + " ObjectID: " + str(outList[0]) + " Order: " + str(outList[5]) # For Testing
            if row[0] == outList[0]:
                # If the ObjectID for the list in the list container
                # for the matching CCL_LRS equals the OBJECTID
                # field in the cursor row, update the
                # cursor row's RESOLUTION_ORDER field
                # to be the same as that list's
                # resolution order field.
                row[2] = outList[5]
            else:
                pass
        cursor.updateRow(row)
                
    if cursor:
        del cursor
    else:
        pass
    if row:
        del row
    else:
        pass
    
###############################################################################
# Future Project: Extend to include a field and sorting for maintenance order.
# Add the MAINTENANCE_ORDER field
###AddField_management(connection1+"CCL_Report", "Maintenance_Order", "SHORT")
###############################################################################
#def ReportMaintenanceOrdering():

# Need to change the calibration points location to the CCL_TEST sde.
def Create_CCL_Calibration_Points():
    # Intersect GIS.City_Limits with SMLRS to obtain points layer
    # write to file geodatabase.
    MakeFeatureLayer_management(stateroutelyr, "smlrs_d")
    MakeFeatureLayer_management(citylimits, "citylimits_d", "TYPE IN ( 'CS', 'ON')")
    intersectFeaures = ["smlrs_d", "citylimits_d"]
    print "Intersecting State Routes and City Limits"
    Intersect_analysis(intersectFeaures, r"D:\workspaces\pythontests.gdb\cal_points_multi", "NO_FID", "", "point")
    
    # Split the multipoint features into single points and place in another layer.
    print "Splitting multipart points into single points."
    MultipartToSinglepart_management(r"D:\workspaces\pythontests.gdb\cal_points_multi", r"D:\workspaces\pythontests.gdb\cal_points_simple")
    
    # Clean the simple points layer by removing extraneous fields.
    
    # Locate the created points layer along the SMLRS routes to
    # generate a table with measurements.
    print "Locating the edge of city boundary points along the state system."
    reloc_properties = "point_LRS POINT point_Loc"
    
    #fieldList = ListFields("smlrs_d")
    #for field in fieldList:
        #print str(field.name)
        
    LocateFeaturesAlongRoutes_lr(r"D:\workspaces\pythontests.gdb\cal_points_simple", "smlrs_d", "LRS_ROUTE", "10 Feet", 
                                 r"D:\workspaces\pythontests.gdb\cal_points_reloc", reloc_properties, "FIRST", "NO_DISTANCE", "NO_ZERO",
                                 "NO_FIELDS")
    
    point_Properties = "point_LRS POINT point_Loc"
    MakeRouteEventLayer_lr("smlrs_d", "LRS_ROUTE", r"D:\workspaces\pythontests.gdb\cal_points_reloc", 
                           point_Properties, "new_point_locations")
    
    CopyFeatures_management("new_point_locations", r"D:\workspaces\pythontests.gdb\CCL_Point_Calibrators")
    
    # Use this set of points as the calibration points for the 
    # CCL_LRS_ROUTE layer's calibration.
    
    # Add the measure values to the points layer so that it can be
    # used to calibrate the measures of the CCL_LRS routes.
    print "Calibration Points created."


def ScriptStatusLogging(taskName = 'Unavailable', taskTarget = 'Unknown',
                        completionStatus = scriptFailure, taskStartDateTime = datetime.datetime.now(), 
                        taskEndDateTime = datetime.datetime.now(), completionMessage = 'Unexpected Error.'):
    # Changed to run on SQL Server instead of trying to share a couple logging tables with gatetest.
    # Also add case for incorrect completion statuses.
    try:
        print 'Script status logging started.'
        
        # Calculate task duration and format it for insertion.
        # Duration should only be 00:00:00 when the information is
        # not correct.
        taskDuration = FindDuration(taskEndDateTime, taskStartDateTime)
        
        # Change the datetimes to ISO 8601 Format (YYYY-MM-DD HH:MM:SS).
        dtStartTimeStamp = CreateTimeStamp(taskStartDateTime)
        
        dtEndTimeStamp = CreateTimeStamp(taskEndDateTime)
        
        processFC = r'D:\Workspaces\CityConnectingLinkTEST\countyMapsSQLSDE.sde\countyMaps.SDE.pythonLogging'
        processFieldList = ['Process_Name','Table_Name', 'Status', 'Start_Date', # Status 0x0 = Success, 0x1 = Failure.
                         'Completion_Date', 'Execution_Time', 'Process_Message']
        
        # Choose the logging table to write to based on the completion status.
        if completionStatus == scriptSuccess or completionStatus == scriptFailure: # Received the correct status format.
            
            # Create the row to be inserted and fill it with the proper values.
            newRow = [taskName, taskTarget, completionStatus, dtStartTimeStamp, dtEndTimeStamp, taskDuration, completionMessage]
            
            cursor = da.InsertCursor(processFC, processFieldList)  # @UndefinedVariable
            newRowNumber = cursor.insertRow(newRow)
            
            if 'cursor' in locals():
                del cursor
            else:
                pass
            
            print "Inserted a new row with ObjectID of: " + str(newRowNumber)
            
        else: # Status format is incorrect.
            print "Received incorrect status information. Will not write to the logging table."
        
    except:
        print 'Script status logging failed.'
        print sys.exc_info()[0], " ",  sys.exc_info()[1], " ", sys.exc_info()[2]
        print(GetMessages(2))
    finally:
        if 'cursor' in locals():
            del cursor
        else:
            pass
    
    print 'Script status logging completed.'


def gateTestCleanup():
    try:
        #########################################################
        # DO NOT USE cx_Oracle DELETE on ESRI registered tables.#
        # Use ESRI tools to delete the rows instead.            #
        #########################################################
        deleteList = xrange(4581, 5639)
        
        gateTestConn = cx_Oracle.connect('gate/data@GATETEST')
        
        firstQuery = """SELECT *
            FROM GATE.PROCESS_LOG"""
        
        #cur1 = sdedev.cursor()
        #cur1.execute(delrows)
        
        cursor1 = gateTestConn.cursor()
        cursor1.execute(firstQuery)
        
        rows = cursor1.fetchall()
        
        for row in rows:
            if row[0] in deleteList:
                print row[0], row[1]
                delQuery = """DELETE FROM GATE.PROCESS_LOG
                WHERE PROCESS_LOG_ID=""" + """'""" + str(row[0]) + """'"""
                print delQuery
                cursor1.execute(delQuery)
                gateTestConn.commit()
            
        cursor1.close()
        
        gateTestConn.close()
        
        if 'cursor1' in locals():
            del cursor1
        else:
            pass
        if 'gateTestConn' in locals():
            del gateTestConn
        else:
            pass
    except:
        print(GetMessages(2))
        if 'cursor1' in locals():
            del cursor1
        else:
            pass
        if 'gateTestConn' in locals():
            del gateTestConn
        else:
            pass
        

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


def CreateTimeStamp(inDateTime):
    #Takes a datetime.datetime object and returns
    #the ISO 8601 Timestamp equivalent.
    
    inDateHour = inDateTime.strftime('%I')
    
    iso8601TimeStamp = (str(inDateTime.year).zfill(4) + '-' + str(inDateTime.month).zfill(2) +
                        '-' + str(inDateTime.day).zfill(2) +
                        ' ' + str(inDateHour).zfill(2) + ":" + str(inDateTime.minute).zfill(2) +
                        ":" + str(inDateTime.second).zfill(2))
    
    '''
    timeDescription = inDateTime.strftime('%p')
    dtOracleTimeStamp = (str(inDateTime.month) + '/' + str(inDateTime.day) + '/' + str(inDateTime.year) + 
                      ' ' + str(inDateHour) + ":" + str(inDateTime.minute) + ":" + 
                      str(inDateTime.second) + ' ' + timeDescription)
    '''
    
    return iso8601TimeStamp


def ListSplitAndSelect():
    ## Fragment used for testing, will not execute properly on its own.
    
    delcount = GetCount_management(r'Database Connections\CANT_CPMS.sde\CPMS.CPMS_FMIS_GIS_DEL_ROWS')
    print str(delcount)+" records to delete"
    deletelist=list()
    ## Only portion below changed.
    if (not True): # Production version tests for delcount threshold.
        pass

    else: #ORA 01795 - Oracle limited to 1000 statements with select in *
        MakeTableView_management(FMIS_LOAD, "FMIS_TABLE")  # @UndefinedVariable
        MakeTableView_management(deltbl, "deletes")  # @UndefinedVariable
        with da.SearchCursor(deltbl, "PROJECT_NUMBER") as delcur:  # @UndefinedVariable
            for row in delcur:
                DelXID=  ("{0}".format(row[0]))
                #print DelXID + " is being deleted from the FMIS table"
                #AddJoin_management(layer_name,"CROSSINGID", deltbl, "CROSSINGID", "KEEP_ALL")
                #delsel = "PROJECT_NUMBER LIKE '"+DelXID+"'"
                #print delsel
                deletelist.append(DelXID)
                #SelectLayerByAttribute_management("FMIS_TABLE", "ADD_TO_SELECTION", delsel) #delsel not yet defined
                #SelectLayerByAttribute_management("FMIS_TABLE","ADD_TO_SELECTION", delsel)
        #print str(deletelist)
                
        #Take care of > 1000 selection issue here by splitting the long list into a series of lists.
        
        maxListSize = 999
        listStart = 0
        listEnd = maxListSize
        i = 0
        curListSize = len(deletelist)
        loopNumber = mathCeil(curListSize / maxListSize)
        firstContainer = list()
        
        # Creates the list container that holds the lists with the project numbers.
        while i <= loopNumber:
            if listEnd > curListSize:
                listEnd = curListSize
            else:
                pass
            listToHold = deletelist[listStart:listEnd]
            firstContainer.append(listToHold)
            i += 1
            listStart = listEnd
            listEnd = listEnd + maxListSize
        
        for secondContainer in firstContainer:
            delsel = "PROJECT_NUMBER IN ("
            for projectNum in secondContainer:
                delsel = delsel + """'"""+projectNum+"""', """
            delsel = delsel[:-2] # Slice that removes the last comma and trailing space.
            delsel = delsel + ")" # Adds the closing parenthesis.
            SelectLayerByAttribute_management("FMIS_TABLE", "ADD_TO_SELECTION", delsel) # ADD_TO_SELECTION works like NEW_SELECTION when no current selection.
            print delsel
        
        countResult = GetCount_management("FMIS_TABLE")
        countNum = int(countResult.getOutput(0))
        print countNum
        
        #DeleteRows_management("FMIS_TABLE")
    print "Delete function completed"


if __name__ == '__main__':
    try:
        #ScriptStatusLogging('dt_functions', 'Connection Test',
        #                    scriptSuccess, datetime.datetime.now(),
        #                    datetime.datetime.now(), 'Test completed.')
        
        #ReportInsertCursor()
        #Create_CCL_Calibration_Points()
        #ListSplitAndSelect()
        #ReportResolutionOrdering()
        pass
    except:
        pass