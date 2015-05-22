#!/usr/bin/env python
# UniqueRoadIdentifierForComplexRouteSegments.py
# This file takes the routes that would otherwise
# be complex and have the same LRS key
# and then assigns them a unique number to make
# sure that they are considered unique and
# do not mess up the routing functions.
# Created 2014-10-23 at 12:18:23 by Dirk Talley
# Last Updated 2014-10-23 at 12:56:55 by Dirk Talley

# SearchCursor to read in the centerline data
# Kyle's Where Clause to separate out routes that would be complex if not separated.
# Logic to add a unique identifier, starting at 1 (0 is the main route)
# UpdateCursor to add the unique identify to those routes, and update their LRS key.

# MakeFeatureLayer_management(lyr,"RCL_Particles",where_clause="COUNTY_L = COUNTY_R AND STATE_L = STATE_R \
# AND ( L_F_ADD =0 OR L_T_ADD =0 OR R_F_ADD =0 OR R_T_ADD =0)")

from arcpy import env
from arcpy.da import SearchCursor as daSearchCursor, UpdateCursor as daUpdateCursor, Editor as daEditor

#env.workspace = r"\\gisdata\arcgis\GISdata\DASC\NG911\KDOTReview\CN_NG911.gdb"
env.workspace = r"C:\gis\geodatabases\CN_NG911.gdb"

inFeatures = r"RoadCenterline"

uniqueIdInFields = ["OBJECTID", "COUNTY_L", "COUNTY_R", "STATE_L", "STATE_R", "L_F_ADD", "L_T_ADD", "R_F_ADD", "R_T_ADD", "UNIQUENO", "LRSKEY", "SHAPE_MILES"]
uniqueIdOutFields = ["OBJECTID", "UNIQUENO", "LRSKEY"]

def createUniqueIdentifier(workspaceLocation, featureClassName, inFieldNamesList, outFieldNamesList):
    
    alphabetListForConversion = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", \
        "L", "M", "N", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

    newCursor = daSearchCursor(featureClassName, inFieldNamesList)
    searchList = list()
    for searchRow in newCursor:
        searchList.append(list(searchRow)) # Transforms the row tuple into a list so it can be edited.
    
    if "newCursor" in locals():
        del newCursor
    else:
        pass
    
    matchCount = 0
    
    matchList = list()
    
    for testRow in searchList:
        if (testRow[1] == testRow[2] and testRow[3] == testRow[4] and (str(testRow[5]) == "0" or str(testRow[6]) == "0" or str(testRow[7]) == "0" or str(testRow[8]) == "0")):
            matchCount += 1
            
            matchList.append(testRow)
    
    matchedRowDictionary = dict()
    
    for matchedRow in matchList:
        matchedRowContainer = list()
        # If the key already exists, assign the previous list of lists
        # to the list container, then append the new list
        # before updating the new value to that key in the dictionary.
        if matchedRow[10] in matchedRowDictionary:
            matchedRowContainer = matchedRowDictionary[matchedRow[10]]
            matchedRowContainer.append(matchedRow)
            matchedRowDictionary[matchedRow[10]] = matchedRowContainer
        # Otherwise, the key needs to be created
        # with the value, the list container, having only
        # one list contained within it for now.
        else:
            matchedRowContainer.append(matchedRow)
            matchedRowDictionary[matchedRow[10]] = matchedRowContainer
    
    for LRSKey in matchedRowDictionary:
        outRowContainer = matchedRowDictionary[LRSKey]
        # Sort based on length
        outRowContainer = sorted(outRowContainer, key = lambda sortingRow: sortingRow[11])
        countVariable = 0 # Start at 0 for unique values
        LRSVariable = ""
        for outRowIndex, outRow in enumerate(outRowContainer):
            # Is this the first list/row in the key's list container?
            # If so, then set the Resolution_Order to 0
            if outRowIndex == 0:
                outRow[9] = 0
            else:
                countVariable += 1
                if countVariable in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
                    outRow[9] = countVariable
                elif countVariable >= 10 and countVariable <= 34:
                    outRow[9] = alphabetListForConversion[countVariable - 10] # Converts countVariable to an alpha character, without the letter "O".
                else:
                    print "The count Variable is above 34. Ran out of numbers and letters to use as unique values."
            
            LRSVariable = outRow[10]
            LRSVariableShortened = str(LRSVariable[:-1]) # Returns the LRSVariable without the last character.
            LRSVariable = LRSVariableShortened + str(outRow[9])
            outRow[10] = LRSVariable
            
            outRowString = ""
            
            for outRowElement in outRow:
                outRowString = outRowString + str(outRowElement) + " "
                
            print outRowString
            
            outRowContainer[outRowIndex] = outRow
            
        matchedRowDictionary[LRSKey] = outRowContainer
    
    newEditingSession = daEditor(workspaceLocation)
    newEditingSession.startEditing()
    newEditingSession.startOperation()
    
    newCursor = daUpdateCursor(featureClassName, outFieldNamesList)  # @UndefinedVariable
    for existingRow in newCursor:
        formattedOutRow = list()
        if existingRow[2] in matchedRowDictionary.keys():
            outRowContainer = matchedRowDictionary[existingRow[2]]
            for outRow in outRowContainer:
                if existingRow[0] == outRow[0]: # Test for matching OBJECTID fields.
                    formattedOutRow.append(outRow[0])
                    formattedOutRow.append(outRow[9])
                    formattedOutRow.append(outRow[10])
                    newCursor.updateRow(formattedOutRow)
                else:
                    pass
                    
        else:
            pass
            
    newEditingSession.stopOperation()
    newEditingSession.stopEditing(True)
    
    if "newCursor" in locals():
        del newCursor
    else:
        pass
           
if __name__ == "__main__":
    createUniqueIdentifier(env.workspace, inFeatures, uniqueIdInFields, uniqueIdOutFields)