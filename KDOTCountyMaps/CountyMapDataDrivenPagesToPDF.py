#!/usr/bin/env python
# -*- coding: utf-8 -*-
# CountyMapDataDrivenPagesToPDF.py

## The purpose of this script is to provide
## flow control and related logic for the
## data driven pages export process for
## the county maps.

## There are currently four county map
## MXDs for the quarter inch county maps
## that are to be used with this
## script which act as the Data Driven
## Page templates.

## Quarter Inch Maps:
## countyMapQuarter9x12H.mxd
## countyMapQuarter9x12V.mxd
## countyMapQuarter12x18H.mxd
## countyMapQuarter12x18V.mxd

## There are also four county map
## MXDs for the half inch count maps:

## Half Inch Maps:
## countyMapHalf18x24H.mxd
## countyMapHalf18x24V.mxd
## countyMapHalf24x36H.mxd
## countyMapHalf24x36V.mxd

## Call CountyMapPreprocessing.py first to
## pull the excel data into the geodatabase.

import os
import sys
import arcpy
import arcpy.da as da
from arcpy import env
import arcpy.mapping

import datetime

startingTime = datetime.datetime.now()

print "Starting Time: " + str(startingTime)


mapsFolder = r"\\dt00mh71\Planning\Cart\Maps\MXD\2014_Update"
env.workspace = mapsFolder

# Do I need connections to SDE for this?
# Test in FileGDB first. Maybe 
# on shared since mh71 is nearly full.
# Then move to the new planning server
# after January/whenever the server
# is running and stable.

## -- Should need a table for the DDP geometries/table information/additional fields.
## -- Also need one for the point geometry that will hold the road names/angles for each county.
## Place the points all in the same table, but give them an identifier for the county
## that they came out of, and dynamically display them in the data driven pages
## based on that...
## or have this arcpy script change the query that limits which points show each time
## that the page changes, along with on the first page.
## Remember to refresh the TOC and the Map after changing the
## current data driven page to a something new. -- Especially
## if you filter based on the currently selected
## data driven page entry.


## Not sure that the triple quoted bit is accurate. -- Correct/rephrase.
'''
## Prior to making the pdf maps, copy the SHARED.COUNTIES_DD table from gisprod (sde:oracle$sde:oracle10g:gisprod)
## and perform point label creation from the roads, which are found in... the SHARED.NON_STATE_SYSTEM table in
## sdedev (sde:oracle$sde:oracle11g:sdedev).
## Filter based on the LRS_ADMO where County is found in the records to keep.
'''

## Then, dissolve by name prior to performing road extension/point creation for road names.

## And make sure that only the roads with a County entry that matches the county in question
## are used for the road extension/point creation.
## Excludes City and KDOT/Highway/Interstate roads.
## KDOT/Highway/Interstate should have shields.

## ^ This is a separate script, develop after the base Data Driven Pages export functionality
## for multiple mxds is complete.

## Also add fields to the COUNTIES_DD table that give the map size and orientation for each county, as per
## the Excel File found in the mapsFolder variable.

### TODO: Work on the preprocessing script for this.
### Set it up to pull the information necessary to create the points for each county,
### then create them (might consider making a .lyr file that can be added to each map
### to speed up the distribution of changes throughout each .mxd when there is a change
### to the labeling of the points. Similar to how the parcel label points layer works.)

mxdList = arcpy.ListFiles("*.mxd")
mxd = ""


def FindDuration(endTime, startTime):
    #Takes two datetime.datetime objects, subtracting the 2nd from the first
    #to find the duration between the two.
    duration = endTime - startTime
    print str(duration)
    
    dSeconds = int(duration.seconds)
    durationp1 = str(int(dSeconds // 3600)).zfill(2)
    durationp2 = str(int((dSeconds % 3600) // 60)).zfill(2)
    durationp3 = str(int(dSeconds % 60)).zfill(2)
    durationString = durationp1 + ':' +  durationp2 + ':' + durationp3
    
    print durationString
    return durationString


# Get the map size information from the geodatabase.
searchFC = r'C:\GIS\Python\CountyMaps\CountyMapsTest.gdb\CountyMapSizes'

# Use geometry, name, administrative ownership, 
searchFieldList = ['County','quarterInchSize', 'mapOrientationDir', 'halfInchSize']

countyMapSizesList = list()

cursor = da.SearchCursor(searchFC, searchFieldList)  # @UndefinedVariable
for row in cursor:
    countyMapSizesList.append(list(row))

if 'cursor' in locals():
    del cursor
else:
    pass
if 'row' in locals():
    del row
else:
    pass

# Sort the list based on the County Name values.
countyMapSizesList = sorted(countyMapSizesList, key=lambda countySize: str(countySize[0]))  

for foundMap in mxdList:
    mxd = arcpy.mapping.MapDocument(os.path.join(mapsFolder, foundMap))
    
    dataDrivenPagesObject = mxd.dataDrivenPages
    
    foundMapMXDRemoved = foundMap[:-4]
    
    #print foundMapMXDRemoved
    
    foundMapFormatted = ""    
    if foundMapMXDRemoved[-5] not in str(range(0,10)): # changed from range(0,9) because the 2nd value in range is not inclusive.
        #print "Not -5"
        foundMapFormatted = foundMapMXDRemoved[-4:]
    elif foundMapMXDRemoved[-6] not in str(range(0,10)):
        #print "Not -6"
        foundMapFormatted = foundMapMXDRemoved[-5:]
    elif foundMapMXDRemoved[-7] not in str(range(0,10)):
        #print "Not -7"
        foundMapFormatted = foundMapMXDRemoved[-6:]
    else:
        #print "foundMap format is not any of those."
        pass
        
    foundMapFormatted = str(foundMapFormatted).upper()
    
    #print "foundMapFormatted = " + str(foundMapFormatted)
    
    
    ## Go through the county map size entries
    ## in order and in each, look for a
    ## matching map name for the current mxd
    ## as their quarterInchSize or halfInchSize
    ## column entry.
    
    ## For each one that has the currently
    ## opened mxd as an entry, export it
    ## as PDF from the current mxd.
    
    quarterOrHalfFolder = "quarterInch"
    
    for countyMapSize in countyMapSizesList:
        countyMapName = str(countyMapSize[0])
        ddpPageIndex = dataDrivenPagesObject.getPageIDFromName(countyMapName)
        
        countyMapQuarter = str(str(countyMapSize[1]) + str(countyMapSize[2])).upper()
        countyMapHalf = str(str(countyMapSize[3]) + str(countyMapSize[2])).upper()
        
        outPathPartialString = str(foundMapFormatted) + str(countyMapName) + ".pdf"
        
        PDFOutpath = os.path.join(mapsFolder, outPathPartialString)
        
        if countyMapQuarter == foundMapFormatted:
            quarterOrHalfFolder = "quarterInch"
            #print "ddpPageIndex: " + str(ddpPageIndex)
            #print "CountyMapQuarter: " + str(countyMapQuarter) + " matched map " + str(foundMapFormatted) + " for " + countyMapName + " county."
            # The following two lines change the Data Driven Page to the ddpPageIndex
            # for the county Map Name:
            ddpPageIndex = dataDrivenPagesObject.getPageIDFromName(countyMapName)
            dataDrivenPagesObject.currentPageID = ddpPageIndex
            
            foundMapOutName = foundMapFormatted[:-1]
            foundMapOutName = foundMapOutName.lower()
            
            countyMapOutName = countyMapName + "County" + foundMapOutName
            
            PDFOutpath = os.path.join(mapsFolder, quarterOrHalfFolder, countyMapOutName)
            dataDrivenPagesObject.exportToPDF(PDFOutpath, "CURRENT")
            
        elif countyMapHalf == foundMapFormatted:
            quarterOrHalfFolder = "halfInch"
            #print "ddpPageIndex: " + str(ddpPageIndex)
            #print "CountyMapHalf: " + str(countyMapHalf) + " matched map " + str(foundMapFormatted) + " for " + countyMapName + " county."
            # The following two lines change the Data Driven Page to the ddpPageIndex
            # for the county Map Name:
            ddpPageIndex = dataDrivenPagesObject.getPageIDFromName(countyMapName)
            dataDrivenPagesObject.currentPageID = ddpPageIndex
            
            foundMapOutName = foundMapFormatted[:-1]
            foundMapOutName = foundMapOutName.lower()
            
            countyMapOutName = countyMapName + "County" + foundMapOutName
            
            PDFOutpath = os.path.join(mapsFolder, quarterOrHalfFolder, countyMapOutName)
            dataDrivenPagesObject.exportToPDF(PDFOutpath, "CURRENT")
            
        else:
            pass
        
        
    del mxd
    
    print "" # Newline.
    
    
    # Definitely look at using subprocess/multiprocess.
    # Expected time to export all the PDFs = 5.25 hours.

endingTime = datetime.datetime.now()

scriptDuration = FindDuration(endingTime, startingTime)

print "Starting Time: " + str(startingTime)
print "Ending Time: " + str(endingTime)
print "Elapsed Time: " + scriptDuration