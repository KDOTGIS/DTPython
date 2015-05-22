#!/usr/bin/env python
# -*- coding: utf-8 -*-
# countymapdatadrivenpagestopdfmulti.py

#######################################################################################
#######################################################################################
### Remember to add a .png export (for replacing the .jpg exports on the webpage).#####
### ^^ Completed. See new function definition.                                    #####
#######################################################################################
#######################################################################################

#-------------------------------------------------------------------------
### IMPORTANT:
### When this script is called, you must call it with
### the exact same capitalization
### that the script is saved with.
### Windows and Python will run it just fine
### with any capitalization, but the
### multiprocessing fork script WILL NOT.
#-------------------------------------------------------------------------

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
## pull the excel data into the geodatabase
## as the CountyMapSizes table.

import os
import shutil

import arcpy
import arcpy.da as da
from arcpy import env, GetMessages, Result

import multiprocessing as mp
from multiprocessing import Process, Manager

import datetime

mapsDirectory = r"\\gis\Planning\Cart\Maps\MXD\2014_Update"
env.workspace = mapsDirectory

# Look at changing this this to a local disk location and then copy from that location to
# the F drive location after the subprocesses have completed.

outputDirectory = r"\\gis\Planning\Cart\Maps\MXD\2014_Update"

exportPDFs = 0
exportPNGs = 1
exportPDFsAndPNGs = 2


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


def subProcessMapExports(countyMapSizesList, mapsFolder, outputPDFParentFolder, foundMap, whatToExport):
    """ Multiprocessing version of the CountyMapDataDrivenPagesToPDF script. 
        Uses multiple cores to export pdfs. Should be significantly faster
        than waiting on one core to do all of the processing work on its own."""
    
    #startTime = str(datetime.datetime.now())
    
    # In the county map road name border creation script
    # the results queue needs to have information
    # on the rows, stored in a list format
    # that can be transferred back easily.
    # Since the only output here should be the pdfs
    # there should be no need to pass any such
    # information back to the main process.
    # Instead, we can pass back completion/performance
    # information, if so desired.
    
    
    # The main process assigns an mxd to each
    # created process.
    try:
        
        #print "trying to open" + str(foundMap)
        mxd = arcpy.mapping.MapDocument(os.path.join(mapsFolder, foundMap))
        
        dataDrivenPagesObject = mxd.dataDrivenPages
        
        foundMapMXDRemoved = foundMap[:-4]
        
        #print foundMapMXDRemoved
        
        foundMapFormatted = ""
        
        foundMapFormatted = foundMapMXDRemoved
            
        foundMapFormatted = str(foundMapFormatted).upper()
        
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
            dataDrivenPagesObject.currentPageID = ddpPageIndex
            
            countyMapQuarter = ""
            countyMapHalf = ""
            
            # The following if/elif/else block replaces the old code that chose which
            # map to use for exporting each county as PDFs.
            if str(countyMapSize[4]) == "noMirror":
                countyMapQuarter = "countyMapQuarter" +  str(countyMapSize[1]) + str(countyMapSize[2])
                countyMapHalf = "countyMapHalf" +  str(countyMapSize[3]) + str(countyMapSize[2])
            elif str(countyMapSize[4]) == "yesMirror":
                countyMapQuarter = "countyMapQuarter" +  str(countyMapSize[1]) + str(countyMapSize[2]) + "_Mirror"
                countyMapHalf = "countyMapHalf" +  str(countyMapSize[3]) + str(countyMapSize[2]) + "_Mirror"
            else:
                print "Map mirroring information not populated. Please fix in the main process."
                
            countyMapQuarter = countyMapQuarter.upper()
            countyMapHalf = countyMapHalf.upper()
            
            if countyMapQuarter == foundMapFormatted:
                quarterOrHalfFolder = "quarterInch"
                
                countyMapOutNamePDF = countyMapName + "CountyQt.pdf" #+ foundMapOutName
                countyMapOutNamePNG = countyMapName + "CountyQt.png"
                
                PDFOutpath = os.path.join(outputPDFParentFolder, quarterOrHalfFolder, countyMapOutNamePDF)
                PNGOutpath = os.path.join(outputPDFParentFolder, quarterOrHalfFolder, countyMapOutNamePNG)
                
                # Exporting to png requires a different bit of code than exporting to pdf.
                # Not sure if it should go in the same function or not.
                # Will need to test with/without using the same map.
                
                try:
                    if whatToExport == 0: # export pdfs
                        dataDrivenPagesObject.exportToPDF(PDFOutpath, "CURRENT")
                    elif whatToExport == 1: # export pngs
                        print "Exporting a png to " + PNGOutpath
                        arcpy.mapping.ExportToPNG(mxd, PNGOutpath, "PAGE_LAYOUT", 0, 0, 300)
                    elif whatToExport == 2: # export pngs & pdfs
                        arcpy.mapping.ExportToPNG(mxd, PNGOutpath, "PAGE_LAYOUT", 0, 0, 300)
                        dataDrivenPagesObject.exportToPDF(PDFOutpath, "CURRENT")
                    else:
                        print "whatToExport value not set correctly. Will not export."
                except:
                    if whatToExport == 0: # could not export pdfs
                        print "Could not export. to " + str(PDFOutpath) + "."
                    elif whatToExport == 1: # could not export pngs
                        print "Could not export. to " + str(PNGOutpath) + "."
                    elif whatToExport == 2: # could not export pngs & pdfs
                        print "Could not export. to " + str(PNGOutpath) + "."
                        print "Could not export. to " + str(PDFOutpath) + "."
                    else:
                        print "Could not export."
                    print arcpy.GetMessages()
            
            elif countyMapHalf == foundMapFormatted:
                quarterOrHalfFolder = "halfInch"
                
                countyMapOutNamePDF = countyMapName + "County.pdf" #+ foundMapOutName
                countyMapOutNamePNG = countyMapName + "County.png"
                
                PDFOutpath = os.path.join(outputPDFParentFolder, quarterOrHalfFolder, countyMapOutNamePDF)
                PNGOutpath = os.path.join(outputPDFParentFolder, quarterOrHalfFolder, countyMapOutNamePNG)
                
                try:
                    if whatToExport == 0: # export pdfs
                        dataDrivenPagesObject.exportToPDF(PDFOutpath, "CURRENT")
                    elif whatToExport == 1: # export pngs
                        print "Exporting a png to " + PNGOutpath
                        arcpy.mapping.ExportToPNG(mxd, PNGOutpath, "PAGE_LAYOUT", 0, 0, 300)
                    elif whatToExport == 2: # export pngs & pdfs
                        arcpy.mapping.ExportToPNG(mxd, PNGOutpath, "PAGE_LAYOUT", 0, 0, 300)
                        dataDrivenPagesObject.exportToPDF(PDFOutpath, "CURRENT")
                    else:
                        print "whatToExport value not set correctly. Will not export."
                except:
                    if whatToExport == 0: # could not export pdfs
                        print "Could not export. to " + str(PDFOutpath) + "."
                    elif whatToExport == 1: # could not export pngs
                        print "Could not export. to " + str(PNGOutpath) + "."
                    elif whatToExport == 2: # could not export pngs & pdfs
                        print "Could not export. to " + str(PNGOutpath) + "."
                        print "Could not export. to " + str(PDFOutpath) + "."
                    else:
                        print "Could not export."
                    print arcpy.GetMessages()
            else:
                pass
            
            
        del mxd
        
    except Exception as e:
        # If an error occurred, print line number and error message
        import traceback, sys
        tb = sys.exc_info()[2]
        print "Line %i" % tb.tb_lineno
        print e.message
    
    except:
        print "An error occurred." # Need to get the error from the arcpy object or result to figure out what's going on.
        print arcpy.GetMessages()
        pass
    
    # Definitely look at using subprocess/multiprocess.
    # Expected time to export all the PDFs = 5.25 hours.
    # With multiprocessing, it gets done in about 1.25 hours.
    # Success! -- Well, it still takes a long time, but it's
    # better than taking over half of a business day.


def mainProcessMapExports(mapsLocation, outputLocation, exportValue):
    '''
    Call with arguments in the format of ..., ..., exportValue, where the export value is
    one of the following: exportPDFs, exportPNGs, or exportPDFsAndPNGs.
    These should be imported/defined as exportPDFs = 0,  = 1, exportPDFsAndPNGs = 2.
    '''
    # Dynamically lists the files in the mxd folder (current workspace).
    # Add mirror-copies of the most used mxds.
    
    mapToCopyList = ["countyMapQuarter9x12V", "countyMapQuarter12x18V", "countyMapHalf18x24V", "countyMapHalf24x36V"]
    
    # Need to add the containing directory using os.path.join
    
    for mapToCopy in mapToCopyList:
        originalFileFullPath = os.path.join(mapsLocation, mapToCopy + ".mxd")
        destinationFileFullPath = os.path.join(mapsLocation, mapToCopy + "_Mirror.mxd")
        try:
            shutil.copy2(originalFileFullPath, destinationFileFullPath)
            print "Added " + str(destinationFileFullPath) + " to the filesystem."
        except:
            print "Could not add " + str(destinationFileFullPath) + " to the filesystem."
            print "It may already exist."
    
    mxdList = arcpy.ListFiles("*.mxd")
    
    # Setup the mxdList -- Done Dynamically above.
    #originalMxdList = ["9x12H.mxd", "9x12V.mxd", "12x18H.mxd", "12x18V.mxd", "18x24H.mxd", "18x24V.mxd", "24x36H.mxd", "24x36V.mxd"]
    # Should now include a *V_Mirror.mxd for each *V original to help speed processing.
    
    # Get the map size information from the geodatabase.
    searchFC = r'\\gisdata\ArcGIS\GISdata\GDB\CountyMappingDataMulti.gdb\CountyMapSizes'
    
    # Use geometry, name, administrative ownership, 
    searchFieldList = ['County','quarterInchSize', 'mapOrientationDir', 'halfInchSize']
    
    # Need to add information on how to know if they should be used with the _Mirror.mxd or not.
    # Maybe add a number to the 
    
    countyMapSizeInfo = list()
    
    cursor = da.SearchCursor(searchFC, searchFieldList)  # @UndefinedVariable
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
    
    countyMapQuarter9x12VCounter = 0
    countyMapQuarter12x18VCounter = 0
    countyMapHalf18x24VCounter = 0
    countyMapHalf24x36VCounter = 0
    
    # Add a yesMirror parameter
    # for vertical maps only as horizontal maps
    # are too few in number to really benefit from it.
    for countyMapSize in countyMapSizeInfo:
        countyMapSize.append("noMirror")
        countyMapOrientation = str(countyMapSize[2])
        countyMapSizeQuarterString = str(countyMapSize[1])
        if countyMapSizeQuarterString == "9x12" and countyMapOrientation == "V":
            if countyMapQuarter9x12VCounter % 2 == 0:
                countyMapSize[4] = "yesMirror"
            else:
                pass
            countyMapQuarter9x12VCounter += 1
        elif countyMapSizeQuarterString == "12x18" and countyMapOrientation == "V":
            if countyMapQuarter12x18VCounter % 2 == 0:
                countyMapSize[4] = "yesMirror"
            else:
                pass
            countyMapQuarter12x18VCounter += 1
        else:
            pass
        
        countyMapSizeHalfString = str(countyMapSize[3])
        if countyMapSizeHalfString == "18x24" and countyMapOrientation == "V":
            if countyMapHalf18x24VCounter % 2 == 0:
                countyMapSize[4] = "yesMirror"
            else:
                pass
            countyMapHalf18x24VCounter += 1
        elif countyMapSizeHalfString == "24x36" and countyMapOrientation == "V":
            if countyMapHalf24x36VCounter % 2 == 0:
                countyMapSize[4] = "yesMirror"
            else:
                pass
            countyMapHalf24x36VCounter += 1
        else:
            pass
    
    
    #for countyMapSize in countyMapSizeInfo:
        #print str(countyMapSize[1])
        #print str(countyMapSize[3])
        #print str(countyMapSize[4])
    
    # The sizes now contain information about whether or not they are to
    # be processed using the _Mirror copies of maps. Just need to make 
    # sure that the process knows how to interpret that information.
    
    #outputQueue = mp.Queue()
    
    ### Mirror copy/use has to be setup prior to creating the processes. ###
    
    # Setup a list of processes that we want to run
    processes = [mp.Process(target=subProcessMapExports, args=(countyMapSizeInfo, mapsLocation, outputLocation, targetMapName, exportValue)) for targetMapName in mxdList]
    #old#processes = [mp.Process(target=exportMapPDFs, args=(outputQueue, countyMapSizeInfo, mapsLocation, outputLocation, targetMapName)) for targetMapName in mxdList]
    
    # Consider using pool.map_async(rand_string, mxdList). -- Figure out how to do this without pool also though.
    
    # Run processes
    for p in processes:
        p.start()
    
    # Exit the completed processes
    for p in processes:
        p.join()
    
    # Get process results from the output queue
    #results = [outputQueue.get() for p in processes]
    
    #for resultItem in results:
    #    print (resultItem + "\n " + 
    #    "Retrieved time: " + str(datetime.datetime.now()))
    
    # Remove the _Mirrored maps so that they can be recreated
    # with updated data next time.
    for mapToCopy in mapToCopyList:
        destinationFileFullPath = os.path.join(mapsLocation, mapToCopy + "_Mirror.mxd")
        try:
            os.remove(destinationFileFullPath)
            print "Removed " + str(destinationFileFullPath) + " from the filesystem."
        except:
            print "Could not remove " + str(destinationFileFullPath) + " from the filesystem."
            print "It may be in use or might not exist."


if __name__ == "__main__":
    # try setting up a list of the maps
    # then, call a process for each map.
    
    startingTime = datetime.datetime.now()
    
    
    print "Starting Time: " + str(startingTime)
    
    mainProcessMapExports(mapsDirectory, outputDirectory, exportPNGs)
    
    '''
    # Dynamically lists the files in the mxd folder (current workspace).
    # Add mirror-copies of the most used mxds.
    
    mapToCopyList = ["countyMapQuarter9x12V", "countyMapQuarter12x18V", "countyMapHalf18x24V", "countyMapHalf24x36V"]
    
    # Need to add the containing directory using os.path.join
    
    for mapToCopy in mapToCopyList:
        originalFileFullPath = os.path.join(mapsLocation, mapToCopy + ".mxd")
        destinationFileFullPath = os.path.join(mapsLocation, mapToCopy + "_Mirror.mxd")
        try:
            shutil.copy2(originalFileFullPath, destinationFileFullPath)
            print "Added " + str(destinationFileFullPath) + " to the filesystem."
        except:
            print "Could not add " + str(destinationFileFullPath) + " to the filesystem."
            print "It may already exist."
    
    mxdList = arcpy.ListFiles("*.mxd")
    
    # Setup the mxdList -- Done Dynamically above.
    #originalMxdList = ["9x12H.mxd", "9x12V.mxd", "12x18H.mxd", "12x18V.mxd", "18x24H.mxd", "18x24V.mxd", "24x36H.mxd", "24x36V.mxd"]
    # Should now include a *V_Mirror.mxd for each *V original to help speed processing.
    
    # Get the map size information from the geodatabase.
    searchFC = r'\\gisdata\ArcGIS\GISdata\GDB\CountyMappingDataMulti.gdb\CountyMapSizes'
    
    # Use geometry, name, administrative ownership, 
    searchFieldList = ['County','quarterInchSize', 'mapOrientationDir', 'halfInchSize']
    
    # Need to add information on how to know if they should be used with the _Mirror.mxd or not.
    # Maybe add a number to the 
    
    countyMapSizeInfo = list()
    
    cursor = da.SearchCursor(searchFC, searchFieldList)  # @UndefinedVariable
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
    
    countyMapQuarter9x12VCounter = 0
    countyMapQuarter12x18VCounter = 0
    countyMapHalf18x24VCounter = 0
    countyMapHalf24x36VCounter = 0
    
    # Add a yesMirror parameter
    # for vertical maps only as horizontal maps
    # are too few in number to really benefit from it.
    for countyMapSize in countyMapSizeInfo:
        countyMapSize.append("noMirror")
        countyMapOrientation = str(countyMapSize[2])
        countyMapSizeQuarterString = str(countyMapSize[1])
        if countyMapSizeQuarterString == "9x12" and countyMapOrientation == "V":
            if countyMapQuarter9x12VCounter % 2 == 0:
                countyMapSize[4] = "yesMirror"
            else:
                pass
            countyMapQuarter9x12VCounter += 1
        elif countyMapSizeQuarterString == "12x18" and countyMapOrientation == "V":
            if countyMapQuarter12x18VCounter % 2 == 0:
                countyMapSize[4] = "yesMirror"
            else:
                pass
            countyMapQuarter12x18VCounter += 1
        else:
            pass
        
        countyMapSizeHalfString = str(countyMapSize[3])
        if countyMapSizeHalfString == "18x24" and countyMapOrientation == "V":
            if countyMapHalf18x24VCounter % 2 == 0:
                countyMapSize[4] = "yesMirror"
            else:
                pass
            countyMapHalf18x24VCounter += 1
        elif countyMapSizeHalfString == "24x36" and countyMapOrientation == "V":
            if countyMapHalf24x36VCounter % 2 == 0:
                countyMapSize[4] = "yesMirror"
            else:
                pass
            countyMapHalf24x36VCounter += 1
        else:
            pass
    
    
    for countyMapSize in countyMapSizeInfo:
        print str(countyMapSize[1])
        print str(countyMapSize[3])
        print str(countyMapSize[4])
    
    # The sizes now contain information about whether or not they are to
    # be processed using the _Mirror copies of maps. Just need to make 
    # sure that the process knows how to interpret that information.
    
    #outputQueue = mp.Queue()
    
    ### Mirror copy/use has to be setup prior to creating the processes. ###
    
    # Setup a list of processes that we want to run
    processes = [mp.Process(target=subProcessMapExports, args=(countyMapSizeInfo, mapsLocation, outputLocation, targetMapName)) for targetMapName in mxdList]
    #old#processes = [mp.Process(target=exportMapPDFs, args=(outputQueue, countyMapSizeInfo, mapsLocation, outputLocation, targetMapName)) for targetMapName in mxdList]
    
    # Consider using pool.map_async(rand_string, mxdList). -- Figure out how to do this without pool also though.
    
    # Run processes
    for p in processes:
        p.start()
    
    # Exit the completed processes
    for p in processes:
        p.join()
    
    # Get process results from the output queue
    #results = [outputQueue.get() for p in processes]
    
    #for resultItem in results:
    #    print (resultItem + "\n " + 
    #    "Retrieved time: " + str(datetime.datetime.now()))
    
    # Remove the _Mirrored maps so that they can be recreated
    # with updated data next time.
    for mapToCopy in mapToCopyList:
        destinationFileFullPath = os.path.join(mapsLocation, mapToCopy + "_Mirror.mxd")
        try:
            os.remove(destinationFileFullPath)
            print "Removed " + str(destinationFileFullPath) + " from the filesystem."
        except:
            print "Could not remove " + str(destinationFileFullPath) + " from the filesystem."
            print "It may be in use or might not exist."
    '''
    
    endingTime = datetime.datetime.now()
    
    scriptDuration = FindDuration(endingTime, startingTime)
    
    print "\n" # Newline for better readability.
    print "For the main/complete script portion..."
    print "Starting Time: " + str(startingTime)
    print "Ending Time: " + str(endingTime)
    print "Elapsed Time: " + scriptDuration
    
    # Doesn't work well on dt00ar60. Try on the geoprocessing server, if/when we get one.
    
    # Make a mainProcess & subProcess function, like in countymappdfcompositormulti.py
    # so that you can call it with options for pdf/jpg/png export.
    
    # mainProcessMapExports(mapsFolder, outputFolder, exportType)
    # subProcessMapExports(sizeInfo, mapsFolder, outputFolder, targetMapName, exportType) # sizeInfo and targetMapName assigned by mainProcess...
    
else:
    pass

# Change this to allow for the exporting of pdfs, jpgs, or pdfs + jpgs.
# Also, find out of you can use pngs instead of jpgs on the webpage.

# Next Script: countymappdfcompositormulti.py