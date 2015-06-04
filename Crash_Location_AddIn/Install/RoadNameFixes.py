#!/usr/bin/env python
# -*- coding: utf-8 -*-
# RoadNameFixes.py
# Adapted from scripts created 2014-05-22
# Author: DAT
# Created: 2015-05-14
# Updated: 2015-05-15
################################################################################################
import os
import re
from arcpy import (AddField_management, AddMessage, CreateTable_management, Delete_management, env, Exists, GetParameterAsText,  # @UnusedImport
                    Sort_management)
from arcpy.da import InsertCursor, SearchCursor, UpdateCursor  # @UnresolvedImport


class optionsHolder():  # Defines an empty class to hold assigned attributes.
    pass


optionsInstance = optionsHolder() # Creates an instance of the empty class.

optionsInstance.roadsFeaturesLocation = r'C:\GIS\Geodatabases\Region1_CL_Final_RoadChecks.gdb\NG911\RoadCenterline'
optionsInstance.accidentDataTable = r'C:\GIS\Geodatabases\GC_OFFSET_20150210_TEST.gdb\BARBER_004_Test_3'
optionsInstance.useKDOTFields = False
## GDB Location should be derived from accidentDataWithOffsetOutput location.


def getGDBLocationFromFC(fullFeatureClassPath):
    test1 = os.path.split(fullFeatureClassPath)
    
    if test1[0][-4:] == ".gdb":
        gdbPath = os.path.dirname(fullFeatureClassPath)
    else:
        gdbPath = os.path.dirname(os.path.dirname(fullFeatureClassPath))
    
    return gdbPath


def UpdateOptionsWithParameters(optionsObject):
    try:
        option0 = GetParameterAsText(0)
        option1 = GetParameterAsText(1)
        #option2 = GetParameterAsText(2) -- Not sure what these options were supposed to be for.
        #option3 = GetParameterAsText(3) -- Not sure what these options were supposed to be for.
    except:
        pass
    
    if (option0 is not None and option0 != ""): # Where the roads features are (roadsFeaturesLocation)
        optionsObject.roadsFeaturesLocation = option0
    else:
        pass
    
    if (option1 is not None and option1 != ""): # Base Accident Data Table (accidentDataTable)
        optionsObject.accidentDataTable = option1
    else:
        pass
    
    optionsInstance.gdbPath = getGDBLocationFromFC(optionsObject.roadsFeaturesLocation)
    
    return optionsObject


# Change this function to write the table to in_memory and then return a reference
# to the table to be used in the next function.
# Test by printing out all of the unique road names in the county.

def CreateUniqueRoadNameTable(optionsObject):
    """ From: Kansas_Unique_Road_Name_List_By_County.py
    This is an search cursor that creates an in_memory table listing all
    of the unique road names in a county.
    
    The primary purpose of the table that this function returns
    is to be used by the preAccidentGeocodingUpdate function
    to inflate the road names from 2009 and prior accident
    data that has been truncated to 6 characters or less.
    """
    
    inputCenterlines = optionsObject.roadsFeaturesLocation
    
    try:
        # Set the variables
        # These should be provided by the optionsObject and
        # modified by input parameters
        # (if available how the script was called).
        
        GDBPath = "in_memory"
        env.workspace = "in_memory"
        tableName = "UniqueRoadNames"
        sortedTableName = "UniqueRoadNames_Sorted"
        #fieldName0 = "COUNTY_L"
        #fieldName1 = "COUNTY_R"
        fieldName2 = "RD"
        #fieldLength0 = 25
        #fieldLength1 = 25
        fieldLength2 = 70
        roadList = list()
        newRoadList = list()
        
        cursorFields = ["RD"]
        
        ### If the table already exists, delete it.
        if Exists(tableName):
            Delete_management(tableName)
        else:
            pass
        
        ### Write a new table to the geodatabase.
        CreateTable_management(GDBPath, tableName)
        
        ### Add fields to the new table.
        #AddField_management(tableName, fieldName0, "TEXT", "", "", fieldLength0)
        #AddField_management(tableName, fieldName1, "TEXT", "", "", fieldLength1)
        AddField_management(tableName, fieldName2, "TEXT", "", "", fieldLength2)
        
        # Create a new search cursor to get road names.
        # Repoint this to the passed in parameter for the roads centerline.
        sCursor = SearchCursor(inputCenterlines, cursorFields)
        
        for rowItem in sCursor:
          
            # Place the data into a 2-dimensional list, with the pairs being County Number and Road Name as strings,
            # with County Number padded to 3 spaces with leading zeroes.
            roadListPart = [rowItem[0]]#, rowItem[1],  rowItem[2]]
            
            # Append the current county number and the current road name to the county number/road name list.
            roadList.append(roadListPart)
        
        # Delete cursor to remove locks on the data 
        try:
            del sCursor
        except:
            pass
        
        # Print the first and last item in the roadList.
        AddMessage("roadList first item:")
        AddMessage(str(roadList[0]))
        AddMessage("roadList last item:")
        AddMessage(str(roadList[-1]))
        
        print ""
        
        # Assign only the unique values in roadList to a new list.        
        for i in roadList:
            if (i not in newRoadList):
                newRoadList.append(i)
        
        # Write the newRoadList to the new table using an insert cursor.
        iCursor = InsertCursor(tableName, cursorFields)
        
        # Rewrite this so that it properly uses the information that it iterates over.
        for roadPlaceHolder in newRoadList:
            iCursor.insertRow(roadPlaceHolder)
        
        # Delete cursor to remove locks on the data 
        try:
            del iCursor
        except:
            pass
        
        Sort_management(tableName, sortedTableName, [["RD", "ASCENDING"]])
        
        sCursor = SearchCursor(sortedTableName, cursorFields)
        
        for rowItem in sCursor:
            print str(rowItem[0])# + " " + str(rowItem[1]) + " " + str(rowItem[2])
            
        # Delete cursor to remove locks on the data 
        try:
            del sCursor
        except:
            pass
    
    except Exception as Exception1:
        print str(Exception1[0])
        try:
            del Exception1
        except:
            pass
    
    # Even if the program has an exception, it should still delete the cursor objects.
    finally:
        try:
            del sCursor
        except:
            pass
        try:
            del iCursor
        except:
            pass


def RoadNameRepair(optionsObject):
    
    # Adapted from a previous script created 2014-05-22
    # by Dirk Talley, which was called
    # Pre_Accident_Geocoding_Update_Cursor.py
    
    # This is an update cursor meant to clean up the road names in accident data.
    # It takes the road name information in the target feature set and reformats
    # it in the hope that the newly formatted data will have a higher match rate
    # when geocoded, without the introduction of any new errors.
    
    # For 2009 data in particular, it checks the information in the road database
    # and performs a check to see if there is a partial match on the 6-or-less
    # character road names with the information in the roads table for that
    # county. If it finds one, and only one, match, it changes the output road name
    # from the 6-or-less character name to the full (assumed) name.
    
    # If you get a "string or buffer expected" error message,
    # it is probably due to the script attempting a pattern match
    # on a None-type (<Null> in Arcmap) data entry in the table.
    # Make sure that you check the data for None-type entries.
    
    # The Fifth and Sixth string matching sections 
    # no longer seem to take nearly as long as they
    # had previously. I ascribe this to the usage of
    # .da cursors and the "in_memory" workspace.
    
    try:
        # Set the environment
        env.workspace = "in_memory"
        
        # Set other variables
        uniqueRoadNamesTable = r"in_memory\UniqueRoadNames"
        uniqueRoadNamesTableFields = ["RD"]
        roadNamesList = list()
        accidentData = optionsObject.accidentDataTable 
        
        if optionsInstance.useKDOTFields == True:
            AddMessage('Using KDOT Fields.')
            accidentCursorFields = ["ESRI_OID", "COUNTY_NBR", "ON_ROAD_KDOT_NAME", "ON_ROAD_KDOT_TYPE", "ON_ROAD_KDOT_SFX_DIR",
                                    "AT_ROAD_KDOT_NAME", "AT_ROAD_KDOT_TYPE", "AT_ROAD_KDOT_SFX_DIR", "ON_AT_ROAD_KDOT_INTERSECT",
                                    "ACCIDENT_KEY"]
        else:
            accidentCursorFields = ["ESRI_OID", "COUNTY_NBR", "ON_ROAD_NAME", "ON_ROAD_TYPE", "ON_ROAD_SUFFIX_DIRECTION",
                                    "AT_ROAD_NAME", "AT_ROAD_TYPE", "AT_ROAD_SUFFIX_DIRECTION", "ON_AT_ROAD_INTERSECT",
                                    "ACCIDENT_KEY"]
        
        #accidentCursorFields = ["ESRI_OID", "COUNTY_NBR", "ON_ROAD_NAME", "ON_ROAD_TYPE", "ON_ROAD_SUFFIX_DIRECTION",
        #                        "AT_ROAD_NAME", "AT_ROAD_TYPE", "AT_ROAD_SUFFIX_DIRECTION", "ON_AT_ROAD_INTERSECT",
        #                        "ACCIDENT_KEY"]
        
        onRoadName = ""
        atRoadName = ""
        
        ## Should make a new table, not use the same one and update it.
        
        # Create a new search cursor to read in the data from
        # the uniqueRoadNames table.
        
        # Create a new search cursor to get road names.
        sCursor = SearchCursor(uniqueRoadNamesTable, uniqueRoadNamesTableFields)
        
        # The table used for this cursor should come from
        # the CreateUniqueRoadNameTable function included
        # in this script.
        
        # If the base roads feature layer is updated, or otherwise changes
        # the uniqueRoadNamesTable will need to be run again.
        
        for sRow in sCursor:
            # Place the data into a 2-part list, with the pairs being County Number and Road Name as strings,
            # with County Number padded to 3 spaces with leading zeroes.
            #print "roadNamesListPart = " + str(sRow)
            roadNamesListPart = list(sRow)
            
            # Append the current county number and the current road name to the county number/road name list.
            roadNamesList.append(roadNamesListPart)
        
        try:
            del sCursor
        except:
            pass
        
        ####################################################
        # This script will now begin updates based on      #
        # seven patterns. The patterns are checked against #
        # data strings in the target accident data layer.  #
        # If it find matches, it attempts to make          #
        # updates and/or corrections to the data. If there #
        # is a problem with this script, please uncomment  #
        # the print statements to better watch the         #
        # program flow.                                    #
        ####################################################
        
        # Create the regex patterns to use in the next part,
        # with the update cursor.
        
        firstMatchString = re.compile(r'C\\', re.IGNORECASE)
        secondMatchString = re.compile(r'^County Road [0-9]+/[ensw]', re.IGNORECASE)
        thirdMatchString = re.compile(r'[0-9]+[rnts][dht][a-z][a-z]', re.IGNORECASE)
        fourthMatchString = re.compile(r'[0-9]+[rnts][dht]/[ensw]', re.IGNORECASE)
        # Just a placeholder, the actual fifthMatchString pattern is generated
        # based on data retrieved within the accident table search cursor.
        fifthMatchString = re.compile(r'^WEST', re.IGNORECASE)
        # Just a placeholder, the actual sixthMatchString pattern is generated
        # based on data retrieved within the accident table search cursor.
        sixthMatchString = re.compile(r'^EAST', re.IGNORECASE)
        seventhMatchString = re.compile(r'^[0-9]+\s[t][h]', re.IGNORECASE)
        atMatch = None
        orMatch = None
        
        accListDict = dict()
        
        # Create a new update cursor for the input feature class.
        
        # Use row[2], row.OR_TYPE, row[4]
        # or row[5], row[6], row[7]
        # to see if the names are already populating
        # the correct type and suffix fields for the
        # roads.
        
        # Replace all of these uCursors with an sCursor
        # then use a uCursor to update it
        # or use an iCursor to add them all back
        # into the table after truncating it.
        
        
        sCursor = SearchCursor(accidentData, accidentCursorFields)
        
        for sRow in sCursor:
            #print sRow[0]
            accListDict[sRow[0]] = list(sRow)
        
        try:
            del sCursor
        except:
            pass
        
        
        for accListItem in accListDict.values():
            #print str(roadListKey)
            
            # Perform updates here
            # Check the name of the roads and correct them.
            
            # Need to expand C\Q and C\27 to County Road Q and County Road 27, respectively.
            # Erroneously encoded with a '\' rather than a '/' between the C and other
            # road name characters.
            
            if (accListItem[2] != None):
                orMatch = firstMatchString.match(accListItem[2]) # re.compile(r'C\\', re.IGNORECASE)
                if (orMatch != None):
                    #print "Need to expand the C\ in this OR_NAME2: ", accListItem[2]
                    #print orMatch.end()
                    #print "County Road" + accListItem[2][orMatch.end():]
                    accListItem[2] = "County Road " + accListItem[2][orMatch.end():]
                else:
                    pass
            else:
                pass
            
            if (accListItem[5] != None):
                atMatch = firstMatchString.match(accListItem[5]) # re.compile(r'C\\', re.IGNORECASE)
                if (atMatch != None):
                    #print "Need to expand the C\ in this AT_NAME2: ", accListItem[5]
                    #print atMatch.end()
                    #print "County Road" + accListItem[5][atMatch.end():]
                    accListItem[5] = "County Road " +accListItem[5][atMatch.end():]
                else:
                    pass
            else:
                pass
            
            
            accListDict[accListItem[0]] = accListItem
            
            #print "After county name fix:"
            #print "accListDict[accListItem[0]]'s ON_ROAD_NAME & AT_ROAD_NAME  = " + str(accListDict[accListItem[0]][2]) + " & " + str(accListDict[accListItem[0]][5])
        
        
        print "####################################################"
        print "# End of First String Matching                     #"
        print "####################################################"
        
        
        
        for accListItem in accListDict.values():
            
            # Need to remove slashes, and if they have a
            # trailing directional make sure that it is
            # in the proper field.
            
            # Pattern matches one or more numbers, then
            # a forward slash, then a directional letter.
            if (accListItem[2] != None):
                orMatch = secondMatchString.match(accListItem[2]) # re.compile(r'^County Road [0-9]+/[ensw]', re.IGNORECASE)
                if (orMatch != None):
                    #print "Need to remove the slash and trailing directional from this OR_NAME2: ", accListItem[2]
                    #print "Match ended at: ", orMatch.end()
                    #print orMatch.group(0)[0:orMatch.end()-2] # The County Road without the slash and trailing directional -- Place this back in OR_NAME2
                    #print orMatch.group(0)[-2:-1] # The slash
                    #print orMatch.group(0)[-1:] # The trailing directional -- Check to see if this is the same as OR_SFX, if not, update OR_SFX
                    accListItem[2] = orMatch.group(0)[0:orMatch.end()-2]
                    
                    if (accListItem[4] != orMatch.group(0)[-1:]):
                        #print "OR_SFX does not match the trailing directional in OR_NAME2"
                        accListItem[4] = orMatch.group(0)[-1:]
                    else:
                        pass
                else:
                    pass
            else:
                pass
            
            if (accListItem[5] != None):
                atMatch = secondMatchString.match(accListItem[5]) # re.compile(r'^County Road [0-9]+/[ensw]', re.IGNORECASE)
                if (atMatch != None):
                    #print "Need to remove the slash and trailing directional from this AT_NAME2: ", accListItem[5]
                    #print "Match ended at: ", atMatch.end()
                    #print atMatch.group(0)[0:atMatch.end()-2] # The County Road without the slash and trailing directional -- Place this back in AT_NAME2
                    #print atMatch.group(0)[-2:-1] # The slash
                    #print atMatch.group(0)[-1:] # The trailing directional -- Check to see if this is the same as AT_SFX, if not, update AT_SFX
                    accListItem[5] = atMatch.group(0)[0:atMatch.end()-2]
                    if (accListItem[7] != atMatch.group(0)[-1:]):
                        #print "AT_SFX does not match the trailing directional in AT_NAME2"
                        accListItem[7] = atMatch.group(0)[-1:]
                    else:
                        pass
                else:
                    pass
            else:
                pass
            
            accListDict[accListItem[0]] = accListItem
        
        
        print "####################################################"
        print "# End of Second String Matching                    #"
        print "####################################################"
        
        #print "At the end of third string matching, this is how the road names look:"
        
        atMatch = None
        orMatch = None
        
        for accListItem in accListDict.values():
            
            # Need to separate 2NDST, 14THST and similar ones.
            
            if (accListItem[2] != None):
                orMatch = thirdMatchString.match(accListItem[2]) # thirdMatchString = re.compile(r'[0-9]+[nts][dht][a-z][a-z]', re.IGNORECASE)
                if (orMatch != None):
                    #print "Need to change this from #NDST/#STST/#THST, to #ND/#ST/#TH and have ST in the OR_TYPE field: ", accListItem[2]
                    #print orMatch.end()
                    #print accListItem[2][0:orMatch.end()-2]
                    #print accListItem[2][-2:]
                    accListItem[2] = accListItem[2][0:orMatch.end()-2]
                    if (accListItem[3] != orMatch.group(0)[-2:]):
                        #print "OR_TYPE does not match the TYPE erroneously concatenated in OR_NAME2"
                        #print "New OR_TYPE should be: ", accListItem[2][-2:]
                        accListItem[3] = orMatch.group(0)[-2:]
                    else:
                        pass
                else:
                    pass
            else:
                pass
            
            if (accListItem[5] != None):
                atMatch = thirdMatchString.match(accListItem[5]) # thirdMatchString = re.compile(r'[0-9]+[nts][dht][a-z][a-z]', re.IGNORECASE)
                if (atMatch != None):
                    #print "Need to change this from #NDST/#STST/#THST, to #ND/#ST/#TH and have ST in the AT_TYPE field: ", accListItem[5]
                    #print atMatch.end()
                    #print accListItem[5][0:atMatch.end()-2]
                    #print accListItem[5][-2:]
                    accListItem[5] = accListItem[5][0:atMatch.end()-2]
                    if (accListItem[6] != atMatch.group(0)[-2:]):
                        #print "AT_TYPE does not match the TYPE erroneously concatenated in AT_NAME2"
                        #print "New AT_TYPE should be: ", accListItem[5][-2:]
                        accListItem[6] = atMatch.group(0)[-2:]
                    else:
                        pass
                else:
                    pass
            else:
                pass
            
            accListDict[accListItem[0]] = accListItem
            
            #print "ON_ROAD_NAME & AT_ROAD_NAME  = " + str(accListDict[accListItem[0]][2]) + " & " + str(accListDict[accListItem[0]][5])
        
        print "####################################################"
        print "# End of Third String Matching                     #"
        print "####################################################"
        
        atMatch = None
        orMatch = None
        
        for accListItem in accListDict.values():
        
            # Need to remove /S from 2ND/S, and similar.
            # Check to see if the trailing directional is in the proper field.
            # If not, update the field to be correct.
            
            if (accListItem[2] != None):
                orMatch = fourthMatchString.match(accListItem[2]) # fourthMatchString = re.compile(r'[0-9]+[nts][dht]/[ensw]', re.IGNORECASE)
                if (orMatch != None):
                    #print "Need to remove the slash and trailing directional from this OR_NAME2: ", accListItem[2]
                    #print "Match ended at: ", orMatch.end()
                    #print orMatch.group(0)[0:orMatch.end()-2] # The Street Name without the slash and trailing directional -- Place this back in OR_NAME2
                    #print orMatch.group(0)[-2:-1] # The slash
                    #print orMatch.group(0)[-1:] # The trailing directional -- Check to see if this is the same as OR_SFX, if not, update OR_SFX
                    accListItem[2] = orMatch.group(0)[0:orMatch.end()-2]
                    if (accListItem[4] != orMatch.group(0)[-1:]):
                        #print "OR_SFX does not match the trailing directional in OR_NAME2"
                        accListItem[4] = orMatch.group(0)[-1:]
                    else:
                        pass
                else:
                    pass
            else:
                pass
        
            if (accListItem[5] != None):
                atMatch = fourthMatchString.match(accListItem[5]) # fourthMatchString = re.compile(r'[0-9]+[nts][dht]/[ensw]', re.IGNORECASE)
                if (atMatch != None):
                    #print "Need to remove the slash and trailing directional from this AT_NAME2: ", accListItem[5]
                    #print "Match ended at: ", atMatch.end()
                    #print atMatch.group(0)[0:atMatch.end()-2] # The Street Name without the slash and trailing directional -- Place this back in AT_NAME2
                    #print atMatch.group(0)[-2:-1] # The slash
                    #print atMatch.group(0)[-1:] # The trailing directional -- Check to see if this is the same as AT_SFX, if not, update AT_SFX
                    accListItem[5] = atMatch.group(0)[0:atMatch.end()-2]
                    if (accListItem[7] != atMatch.group(0)[-1:]):
                        #print "AT_SFX does not match the trailing directional in AT_NAME2"
                        accListItem[7] = atMatch.group(0)[-1:]
                    else:
                        pass
                else:
                    pass
            else:
                pass
        
            accListDict[accListItem[0]] = accListItem
        
        
        print "####################################################"
        print "# End of Fourth String Matching                    #"
        print "####################################################"
        
        ### Fifth and Sixth String matching are more complex and
        ### will take more time to rebuild.
        
        ### But, I can probably remove some of the complexity
        ### by making sure that I'm only focused on one county
        ### at a time (Thus removing county checks)
        ### and by making sure that the years are selected for
        ### properly.
        
        atMatch = None
        orMatch = None
        
        for accListItem in accListDict.values():
          
            # If there are problems, try moving orMatch reinitialization here.
            # This cursor updates the on road name (ON_ROAD_NAME) for the
            # accident data if the data is from the year 2009 or before,
            # when the maximum field length for road names was only 6.
            
            if (accListItem[2] != None and (len(accListItem[2]) == 5 or len(accListItem[2]) == 6)):
                try:
                    accYear = accListItem[9][0:4] # Get the first 4 characters of the Accident_Key
                    accYear = int(accYear) # Turn them into an integer.
                except:
                    accYear = 2000 # If there was a problem, assume the accident was from 2000.
                
                if (accYear <= 2009): ## Replaced previous check with this check for accYears which are 2009 .
                    
                    # The next line creates a regex pattern using the current row's AT_ROAD_NAME field
                    # as the pattern, ignoring case.
                    
                    fifthMatchString = re.compile(r'{}'.format(re.escape(accListItem[2])), re.IGNORECASE)
                    #print "This data about", accListItem[2], "is from", int(accListItem.YEAR)
                    roadMatchCounter = 0
                    for roadNamesItem in roadNamesList:
                        noSpacesRoadName = str(roadNamesItem[0]).replace(' ', '')
                        orMatch = fifthMatchString.match(noSpacesRoadName)
                        if (orMatch != None):
                            #print "Found a match for", accListItem[2], "and", roadNamesItem[0]
                            roadMatchCounter += 1
                        else:
                            pass
                    # If there was only one match between the accident road name for that county and the
                    # unique road names for that county, replace the accident road name with the
                    # unique road name. -- Does another loop through the roadList to accomplish
                    # this. Probably not the most efficient way to do this, but it works.
                    if roadMatchCounter == 1:
                        #print "Exactly one road matched in this county. Road Matches: ", roadMatchCounter
                        for roadNamesItem in roadNamesList:        
                            # Make sure that the length of the roadNamesItem's name is 6 or greater
                            # and that it is larger than the accListItem.
                            if len(roadNamesItem[0]) > 5 and len(roadNamesItem[0]) > len(accListItem[2]):
                                noSpacesRoadName = str(roadNamesItem[0]).replace(' ', '')
                                orMatch = fifthMatchString.match(noSpacesRoadName)
                                if (orMatch != None):
                                    AddMessage("Old on road name was: " + str(accListItem[2]))
                                    AddMessage("New on road name will be corrected to: " + str(roadNamesItem[0]).upper())
                                    accListItem[2] = str(roadNamesItem[0]).upper()
                                else:
                                    pass
                            else:
                                pass
                            
                    elif roadMatchCounter > 1:
                        #print "More than one road matched in this county. Road Matches: ", roadMatchCounter
                        pass
                    else:
                        pass
                else:
                    pass
            else:
                pass
            
            accListDict[accListItem[0]] = accListItem
        
        print "####################################################"
        print "# End of Fifth String Matching                     #"
        print "####################################################"
        
        atMatch = None
        orMatch = None
        
        for accListItem in accListDict.values():
          
            # If there are problems, try moving atMatch reinitialization here.
            # This cursor updates the at road name (AT_ROAD_NAME) for the
            # accident data if the data is from the year 2009, when the
            # maximum field length for road names was only 6.
            
            if (accListItem[5] != None and (len(accListItem[5]) == 5 or len(accListItem[5]) == 6)):
                try:
                    accYear = accListItem[9][0:4] # Get the first 4 characters of the Accident_Key
                    accYear = int(accYear) # Turn them into an integer.
                except:
                    accYear = 2000 # If there was a problem, assume the accident was from 2000.
                
                if (accYear <= 2009): ## Replaced previous check with this check for accYears which are 2009 .
                    
                    # The next line creates a regex pattern using the current row's AT_ROAD_NAME field
                    # as the pattern, ignoring case.
                    
                    sixthMatchString = re.compile(r'{}'.format(re.escape(accListItem[5])), re.IGNORECASE)
                    #print "This data about", accListItem[5], "is from", int(accListItem.YEAR)
                    roadMatchCounter = 0
                    for roadNamesItem in roadNamesList:
                        # Removes all the spaces from the roadName, allowing
                        # for matching of UNIONC to UNION CHAPEL, LONETR to LONE TREE,
                        # TRICIT to TRI CITY, etc.
                        noSpacesRoadName = str(roadNamesItem[0]).replace(' ', '')
                        atMatch = sixthMatchString.match(noSpacesRoadName)
                        if (atMatch != None):
                            #print "Found a match for", accListItem[5], "and", roadNamesItem[0]
                            roadMatchCounter += 1
                        else:
                            pass
                    # If there was only one match between the accident road name for that county and the
                    # unique road names for that county, replace the accident road name with the
                    # unique road name. -- Does another loop through the roadList to accomplish
                    # this. Probably not the most efficient way to do this, but it works.
                    if roadMatchCounter == 1:
                        #print "Exactly one road matched in this county. Road Matches: ", roadMatchCounter
                        for roadNamesItem in roadNamesList:        
                            # Make sure that the length of the roadNamesItem's name is 6 or greater
                            # and that it is larger than the accListItem.
                            if len(roadNamesItem[0]) > 5 and len(roadNamesItem[0]) > len(accListItem[5]):
                                noSpacesRoadName = str(roadNamesItem[0]).replace(' ', '')
                                atMatch = sixthMatchString.match(noSpacesRoadName)
                                if (atMatch != None):
                                    AddMessage("Old at road name was: " + str(accListItem[5]))
                                    AddMessage("New at road name will be corrected to: " + str(roadNamesItem[0]).upper())
                                    accListItem[5] = str(roadNamesItem[0]).upper()
                                else:
                                    pass
                            else:
                                pass
                            
                    elif roadMatchCounter > 1:
                        #print "More than one road matched in this county. Road Matches: ", roadMatchCounter
                        pass
                    else:
                        pass
                else:
                    pass
            else:
                pass
            
            accListDict[accListItem[0]] = accListItem
        
        print "####################################################"
        print "# End of Sixth String Matching                     #"
        print "####################################################"
        
        
        for accListItem in accListDict.values():
            
            # Remove the extra space in roads with names like "5 TH" and "17 TH".
            
            if (accListItem[2] != None):
                orMatch = seventhMatchString.match(accListItem[2]) # re.compile(r'^[0-9]+\s[t][h]', re.IGNORECASE)
                if (orMatch != None):
                    #print "Need to remove the extra space between the number and the 'TH' in this ON_ROAD_NAME: ", accListItem[2]
                    #print orMatch.end()
                    #print "County Road" + accListItem[2][orMatch.end():]
                    accListItem[2] = orMatch.group(0)[0:orMatch.end()-3] + orMatch.group(0)[orMatch.end()-2:orMatch.end()]
                    print accListItem[2]
                else:
                    pass
            else:
                pass
            
            if (accListItem[5] != None):
                atMatch = seventhMatchString.match(accListItem[5]) # re.compile(r'^[0-9]+\s[t][h]', re.IGNORECASE)
                if (atMatch != None):
                    #print "Need to remove the extra space between the number and the 'TH' in this AT_ROAD_NAME: ", accListItem[5]
                    #print atMatch.end()
                    #print "County Road" + accListItem[5][atMatch.end():]
                    accListItem[5] = atMatch.group(0)[0:atMatch.end()-3] + atMatch.group(0)[atMatch.end()-2:atMatch.end()]
                    print accListItem[5]
                else:
                    pass
            else:
                pass
            
            accListDict[accListItem[0]] = accListItem
        
        
        print "####################################################"
        print "# End of Seventh String Matching                   #"
        print "####################################################"
        
        print "####################################################"
        print "# Rebuilding Intersection Names                    #"
        print "####################################################"
        
        for accListItem in accListDict.values():
            
            # Rebuild the intersection names in the form of:
            # onRoadName + " | " + atRoadName
            
            onRoadName = ""
            atRoadName = ""
            
            if accListItem[2] != None:
                onRoadName = str(accListItem[2])
            else:
                pass
            
            if accListItem[5] != None:
                atRoadName = str(accListItem[5])
            else:
                pass
            
            if onRoadName != None and atRoadName != None:
                accListItem[8] = str(onRoadName + " | " + atRoadName)
            else:
                pass
            
            accListDict[accListItem[0]] = accListItem
        
        print "####################################################"
        print "# Intersection Names Rebuilt                       #"
        print "####################################################"
        
        ### Don't forget to add accident_key to the list of sCursor
        ### fields. Need it to properly select which accidents
        ### need their road names un-truncated.
        
        print "####################################################"
        print "# Applying Changes with an Update Cursor           #"
        print "####################################################"
        
        uCursor = UpdateCursor(accidentData, accidentCursorFields)
        
        for uCursorRow in uCursor:
            try:
                accListItem = accListDict[uCursorRow[0]]
                uCursor.updateRow(accListItem)
            except:
                pass        
        try:
            del uCursor
        except:
            pass
        
        print "####################################################"
        print "# Update completed.                                #"
        print "####################################################"
        
        
    except Exception as newException:
        print str(newException)
        del newException
    
    
    finally:
        try:
            del sCursor
        except:
            pass
        try:
            del uCursor
        except:
            pass

if __name__ == "__main__":
    optionsInstance = UpdateOptionsWithParameters(optionsInstance)
    CreateUniqueRoadNameTable(optionsInstance)
    # Successfully matches 5 character names to
    # multi-word names where the 6th character is
    # a space. -- Might need more work to get the
    # function to look at roadnames like BLACKG
    # and BLACKK to match them with BLACK GOLD
    # and BLACK K as that would require
    # inserting a space between the 5th and 6th
    # character on reach road name that was exactly
    # six characters long, then attempting to 
    # do all of the matching functions with the
    # space-inserted road name.
    #
    ## Need to run this twice. Once for the non-KDOT fields
    ## and then again for KDOT fields.
    # Set optionsInstance to use the non-KDOT fields.
    RoadNameRepair(optionsInstance)
    # Change optionsInstance to use the KDOT fields
    # and then run the RoadNameRepair function again.
    optionsInstance.useKDOTFields = True
    RoadNameRepair(optionsInstance)
    AddMessage("Road Name Fixes complete.")
else:
    pass