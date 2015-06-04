#!/usr/bin/env python
# -*- coding: utf-8 -*-
# geoprocesscountymaptopdf.py
'''
@author: dtalley
Created: 2015-06-03
'''


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
## pull the excel data into the geodatabase
## as the CountyMapSizes table.
##
## -- Change this to a sql server instance.
### Get the sql server instance fixed so that you have the users that you want in it
### and things run through the gisAutomation user/data owner instead of SDE.

import os
import sys

import arcpy.da as da
from arcpy import env, GetMessages, GetParameterAsText, mapping

import datetime

mapsDirectory = r"\\gisdata\Planning\Cart\Maps\MXD\2014_Update"
env.workspace = mapsDirectory
countyMapSizesPath = r'\\gisdata\ArcGIS\GISdata\GDB\CountyMappingDataMulti.gdb\CountyMapSizes'

# Look at changing this this to a local disk location and then copy from that location to
# the F drive location after the subprocesses have completed.

outputDirectory = r"\\gisdata\Planning\Cart\Maps\MXD\2014_Update\tempOutputTest"

exportPDFs = 0
exportPNGs = 1
exportPDFsAndPNGs = 2


class optionsHolder():  # Defines an empty class to hold assigned attributes.
    pass


optionsInstance = optionsHolder() # Creates an instance of the empty class.


def UpdateOptionsWithParameters(optionsObject):
    try:
        option0 = GetParameterAsText(0)
        option1 = GetParameterAsText(1)
        
    except:
        pass
    
    if (option0 is not None and option0 != ""):
        optionsObject.countyName = option0
    else:
        optionsObject.countyName = "Harvey"
    
    if (option1 is not None and option1 == "quarterInch"): # Name of the Address Locator
        optionsObject.mapScale = option1
    else:
        optionsObject.mapScale = "halfInch"
    
    return optionsObject


def FindDuration(endTime, startTime):
    #Takes two datetime.datetime objects, subtracting the 2nd from the first
    #to find the duration between the two.
    duration = endTime - startTime
    #print str(duration)
    
    dSeconds = int(duration.seconds)
    durationp1 = str(int(dSeconds // 3600)).zfill(2)
    durationp2 = str(int((dSeconds % 3600) // 60)).zfill(2)
    durationp3 = str(int(dSeconds % 60)).zfill(2)
    durationString = durationp1 + ':' +  durationp2 + ':' + durationp3
    
    return durationString
 

def geoprocessMapExport(countyMapSizesLocation, mapsFolder, outputPDFParentFolder, optionsObject):
    """ Geoprocessing version of the CountyMapDataDrivenPagesToPDF script.
    """
    
    # Probably fastest to just rewrite this from scratch/samples. Don't actually need most of what's
    # going on here except the ability to select a map based on the name/size list.
    # That's about it. The rest of the function is overly complicated for the process.
    # Not sure yet if I'm going to write a function to spawn map copies for each county which will
    # preset the map to that data driven page so that it's on the right one as soon as it opens,
    # or if I'm going to use the data driven pages to set the data driven page on each call of the
    # script after opening the proper map document. -- The second approach seems like a better one
    # but the first just has the disadvantage of creating many more map documents, which are essentially
    # just data taking up a bit of disk space. -- It is also slightly more difficult to maintain
    # as the documents have to be deleted/recreated when there is a change to any of the template
    # map documents. -- However, if there were to be multiple print calls of the same Map Scale for
    # different counties in a short period of time, the second approach is probably better, since it
    # assures a different map is used for each function call -- Possible solution is to preCopy the
    # template maps to a different location and append a randomly generated number which is highly
    # likely to be unique (and if not, should cause a failure, which can be checked for and allow a separate
    # attempt to copy the map) prior to actually opening them with the script and then exporting the pdf.
    
    # Only need to get the maps location, the requested scale, the requested county name, the table
    # to translate between the two of them, and the place to output the PDF.
    
    # In the county map road name border creation script
    # the results queue needs to have information
    # on the rows, stored in a list format
    # that can be transferred back easily.
    # Since the only output here should be the pdfs
    # there should be no need to pass any such
    # information back to the main process.
    # Instead, we can pass back completion/performance
    # information, if so desired.
    
    # Get the map size information from the geodatabase.
    ### This needs to be change away from a networked .gdb to the sql server instance.
    ### Of course, I also need to get my GIS automation data owner set up.
    
    searchFieldList = ['County','quarterInchSize', 'mapOrientationDir', 'halfInchSize']
    
    countyMapSizeInfo = list()
    
    cursor = da.SearchCursor(countyMapSizesLocation, searchFieldList)  # @UndefinedVariable
    for row in cursor:
        countyMapSizeInfo.append(list(row))
    
    if 'cursor' in locals():
        del cursor
    else:
        pass
    if 'row' in locals():
        del row
    else:
        pass
    
    # Sort the list based on the County Name values.
    countyMapSizeInfo = sorted(countyMapSizeInfo, key=lambda countySize: str(countySize[0]))
    
    # Generate the map's name from the countyMapSizeInfo, the county's name and the given scale.
    # The path is given from the maps folders location.
    # Then, just need to open the map, set it to the correct data driven page, and export a pdf.
    ## ^ May change this to opening the map which is already set to the correct data driven
    ## page in the future, but that requires a separate script to pre-make those and slightly
    ## complicates the process, so this is a better way to test first even though the performance
    ## might not be as good.
    
    countyToUse = optionsObject.countyName 
    
    scaleToUse = optionsObject.mapScale
    
    try:
        for countyMapSizeItem in countyMapSizeInfo:
            if countyMapSizeItem[0].lower() == countyToUse.lower():
                if (scaleToUse.lower() == "halfInch".lower()):
                    mapToUse = "countyMapHalf" + countyMapSizeItem[3] + countyMapSizeItem[2] + ".mxd"
                    countyMapOutNamePDF = countyToUse + "County.pdf"
                else:
                    mapToUse = "countyMapQuarter" + countyMapSizeItem[1] + countyMapSizeItem[2] + ".mxd"
                    countyMapOutNamePDF = countyToUse + "CountyQt.pdf"
            else:
                pass
            
        
    except:
        pass
    
    try:
        
        print "Trying to open " + str(mapToUse) + " in " +  str(mapsFolder) + "."
        mxd = mapping.MapDocument(os.path.join(mapsFolder, mapToUse))
        
        dataDrivenPagesObject = mxd.dataDrivenPages        
        
        ## Just need to open the mapToUse and set it's data driven
        ## page, then export, using the mapScale to direct the output.
         
        PDFOutpath = os.path.join(outputPDFParentFolder, scaleToUse, countyMapOutNamePDF)
        ddpPageIndex = dataDrivenPagesObject.getPageIDFromName(countyToUse)
        dataDrivenPagesObject.currentPageID = ddpPageIndex
        dataDrivenPagesObject.exportToPDF(PDFOutpath, "CURRENT")
        
        
        try:
            del mxd
        except:
            pass
        
    except Exception as exceptionInstance:
        # If an error occurred, print line number and error message
        tb = sys.exc_info()[2]
        print "Line %i" % tb.tb_lineno
        print exceptionInstance.message
        
        print "An error occurred." # Need to get the error from the arcpy object or result to figure out what's going on.
        print GetMessages()
        
        try:
            del exceptionInstance
        except:
            pass


if __name__ == "__main__":
    # try setting up a list of the maps
    # then, call a process for each map.
    
    UpdateOptionsWithParameters(optionsInstance)
    
    startingTime = datetime.datetime.now()
    
    # need to get the options from the script parameters somewhere around here
    
    print "Starting Time: " + str(startingTime)
    
    # mapsDirectory, outputDirectory exist as variables
    # need to modify the function signature for the geoprocessMapExport function so that it is able to
    # accept those variables, as well as the countyName, and the requestedMapScale.
    
    geoprocessMapExport(countyMapSizesPath, mapsDirectory, outputDirectory, optionsInstance)
    
    endingTime = datetime.datetime.now()
    
    scriptDuration = FindDuration(endingTime, startingTime)
    
    print "\n" # Newline for better readability.
    print "For the export script..."
    print "Starting Time: " + str(startingTime)
    print "Ending Time: " + str(endingTime)
    print "Elapsed Time: " + scriptDuration
    
else:
    pass