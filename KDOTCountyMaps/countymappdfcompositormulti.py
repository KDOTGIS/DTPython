#!/usr/bin/env python
# -*- coding: utf-8 -*-
# countymappdfcompositor.py

## This script is meant to take a pdf and format it for printing on a 36" wide roll.
## To do this, it needs to take a pdf as input.
## Then, it needs to get the height and width of the pdf.
## If either of these are factors of 36, then
## find out how many times each goes into 36 evenly.

## Prefer to have 3, then 2, then <other> number of times
## that a height or width measurement goes into 36 evenly.

## Rotate the pdfs such that the side with a measurement
## which is a factor of 36 is now the pdf's width.

## Place that pdf in position 1, place a 2nd copy
## of that pdf in position 2.

## If the total width does not equal 36, place
## a 3rd copy in position 3.

## If, for some reason, the total width still
## does not equal 36, check to make sure
## that when a 4th copy is placed into
## position 4, that the width will equal
## 36. If so, place the 4th copy in
## position 4.

## If the total width would not equal 36
## after 4 copies, complain and exit.

## Using the PyPDF2 library.
import PyPDF2 #-- See saved page on merge. -- Remember to change all (4?) of the bounding boxes when you do this.
import os
import sys
from PyPDF2 import PdfFileWriter, PdfFileReader

import multiprocessing as mp
from multiprocessing import Process, Manager

import datetime

print "Imports complete."

# Make a function, then call it with both input folders.

inputFolder1 = r"\\gis\planning\Cart\Maps\MXD\2014_Update\quarterInch"
outputFolder1 = r"\\gis\planning\Cart\Maps\MXD\2014_Update\quarterInch\Composited"
#outputFolder1 = r"C:\GIS\Python\CountyMaps\CompositeMultiTest"

inputFolder2 = r"\\gis\planning\Cart\Maps\MXD\2014_Update\halfInch"
outputFolder2 = r"\\gis\planning\Cart\Maps\MXD\2014_Update\halfInch\Composited"
#outputFolder2 = r"C:\GIS\Python\CountyMaps\CompositeMultiTest"

def subProcessPDFCompositor(inputFolderForComposites, outputFolderForComposites, pdfsToCompositeList):
    '''
    inputFileList = os.listdir(inputFolderToComposite)
    
    inputFileListCleaned = list()
    
    # Clean the list of non-pdf files.
    for inputFile1 in inputFileList:
        if inputFile1[-4:] == ".pdf":
            inputFileListCleaned.append(inputFile1)
            print "keeping: " + str(inputFile1)
        else:
            print "not keeping: " + str(inputFile1)
            pass
            #inputFileList.remove(inputFile1)
    '''
    
    for inputFile1 in pdfsToCompositeList:
        compositeValue = 1
        
        print inputFile1
        inputPath1 = os.path.join(inputFolderForComposites, inputFile1)
        
        outputPath1 = os.path.join(outputFolderForComposites, (inputFile1[:-4] + "Composited.pdf"))
        
        #print ("Compositor input = " + inputPath1)
        input1 = PdfFileReader(open(inputPath1, "rb"))
        input2 = PdfFileReader(open(inputPath1, "rb"))
        outputWriter = PdfFileWriter()
        
        inputData1 = input1.getPage(0)
        inputData2 = input2.getPage(0)
        
        xDimensionForMediaBox = inputData1.mediaBox.getUpperRight_x()
        yDimensionForMediaBox = inputData1.mediaBox.getUpperRight_y()
        
        if xDimensionForMediaBox == (72 * 12):
            # No rotation needed, place 3 side by side.
            inputData1.mergeTranslatedPage(inputData2, inputData1.mediaBox.getUpperRight_x(), 0, True)
            inputData1.mergeTranslatedPage(inputData2, inputData1.mediaBox.getUpperRight_x(), 0, True)
            
        elif yDimensionForMediaBox == (72 * 12):
            # Rotate 90 degrees, place 3 side by side.
            inputData1.rotateClockwise(90)
            inputData2.rotateClockwise(90)
            
            inputData1.mergeTranslatedPage(inputData2, 0, inputData1.mediaBox.getUpperRight_y(), True)
            inputData1.mergeTranslatedPage(inputData2, 0, inputData1.mediaBox.getUpperRight_y(), True)
            
        elif xDimensionForMediaBox == (72 * 18):
            # No rotation needed, place 2 side by side.
            inputData1.mergeTranslatedPage(inputData2, inputData1.mediaBox.getUpperRight_x(), 0, True)
            
        elif yDimensionForMediaBox == (72 * 18):
            # Rotate 90 degrees, place 2 side by side.
            inputData1.rotateClockwise(90)
            inputData2.rotateClockwise(90)
            
            inputData1.mergeTranslatedPage(inputData2, 0, inputData1.mediaBox.getUpperRight_y(), True)
            
        elif xDimensionForMediaBox == (72 * 36):
            # No changes needed, write to output.
            pass
        elif yDimensionForMediaBox == (72 * 36):
            # Rotate 90 degrees, write to output.
            inputData1.rotateClockwise(90)
            
        else:
            print "PDF dimensions are not in the expected range. Will not composite for:" + str(inputFile1)
            compositeValue = 0
        
        boundingRectangle1 = inputData1.mediaBox
        inputData1.artBox = boundingRectangle1
        inputData1.bleedBox = boundingRectangle1
        inputData1.cropBox = boundingRectangle1
        inputData1.trimBox = boundingRectangle1
        
        if compositeValue == 1:
            try:
                outputWriter.addPage(inputData1)
                sys.stdout.flush()
                
                #print("Writing " + outputPath1)
                outputStream = file(outputPath1, "wb")
                outputWriter.write(outputStream)
                #print("Done writing "  + outputPath1)
            except:
                print("Could not write " + outputPath1)
        else:
            pass
        
        if "input1" in locals():
            del input1
        else:
            pass
        
        if "input2" in locals():
            del input2
        else:
            pass
            
        if "outputWriter" in locals():
            del outputWriter
        else:
            pass

# For some reason, this code ran much faster for the half inch versions than it did for the quarter inch
# versions. Is rotating/merging the pdf an additional time really that expensive of an operation?
# -- I think it's actually the reading/rereading of the pdf that is causing the slowdown here.

# Could maybe move to using underscores or similar. Definitely need to make shorter names, however.
# Might start abbreviating things just a bit instead of spelling things out as I have been doing.

# Could call things cm_* instead of CountyMap* or CountyMaps* - Would make it easier to keep the.
# naming consistent then as well as there would be no problem with plurality consistency.


# The following seems to be a good way to split a list into multiple lists:
#for x in range(0, splitNumber):
#    pdfsToCompositeList = list()
#    fileCounter = 0
#    for inputFile in inputFileListCleaned:
#        if (fileCounter % splitNumber) == x:
#            pdfsToCompositeList.append(inputFile)
#        else:
#            pass
#        fileCounter += 1
#    pdfsToCompositeContainer.append(pdfsToCompositeList)

# Map Settings Change:
# Changed away from: Unchecked Box for Convert Mark Symbols to Polygons.
# Changed to: Checked Box for Convert Mark Symbols to Polygons.


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


def mainProcessPDFCompositor(inputDirectory, outputDirectory):
    inputFolderToUse = inputDirectory
    outputFolderToUse = outputDirectory
    
    # List the pdfs here.
    inputFileList = os.listdir(inputFolderToUse)
    
    inputFileListCleaned = list()
    
    # Clean the list of non-pdf files.
    for inputFile1 in inputFileList:
        if inputFile1[-4:] == ".pdf":
            inputFileListCleaned.append(inputFile1)
            print "keeping: " + str(inputFile1)
        else:
            print "not keeping: " + str(inputFile1)
            pass
            #inputFileList.remove(inputFile1)
    
    #startingTime = datetime.datetime.now()
    
    
    print "Starting Time: " + str(startingTime)
    
    pdfsToCompositeContainer = list()
    
    try:
        coreCount = mp.cpu_count()
    except:
        coreCount = 4
    
    splitNumber = coreCount + 2 # Test performance with +1, and with + 2. If "+ 2" works better, consider "math.Ceil(coreCount * 1.5)"
    
    pdfsToCompositeList = list()
    
    
    # Splits the list into groups of items
    # to composite based on the number of processes
    # that are used (splitNumber).
    for x in range(0, splitNumber):
        pdfsToCompositeList = list()
        fileCounter = 0
        for inputFile in inputFileListCleaned:
            if (fileCounter % splitNumber) == x:
                pdfsToCompositeList.append(inputFile)
            else:
                pass
            fileCounter += 1
        pdfsToCompositeContainer.append(pdfsToCompositeList)
    
    
    # Setup a group of processes (as a list) that we want to run
    # and then pass them the list of pdfs to composite based
    # on the lists that were created with the splitNumber.
    processes = [mp.Process(target=subProcessPDFCompositor, args=(inputFolderToUse, outputFolderToUse, pdfsToComposite)) for pdfsToComposite in pdfsToCompositeContainer]
    #old#processes = [mp.Process(target=exportMapPDFs, args=(outputQueue, countyMapSizeInfo, mapsLocation, outputLocation, targetMapName)) for targetMapName in mxdList]
    
    # Consider using pool.map_async(rand_string, mxdList). -- Figure out how to do this without pool also though.
    
    # Run processes
    for p in processes:
        p.start()
    
    # Exit the completed processes
    for p in processes:
        p.join()
    
    print "\nCompositing complete for " + str(inputDirectory) + "!"


if __name__ == "__main__":
    startingTime = datetime.datetime.now()
    #mainProcessPDFCompositor(inputFolder1, outputFolder1)
    mainProcessPDFCompositor(inputFolder2, outputFolder2)
    print "Script complete."


    '''
if __name__ == "__main__":
    # try setting up a list of the maps
    # then, call a process for each map.
    
    # Setup the mxdList -- Done Dynamically at the top.
    #mxdList = ["9x12H.mxd", "9x12V.mxd", "12x18H.mxd", "12x18V.mxd", "18x24H.mxd", "18x24V.mxd", "24x36H.mxd", "24x36V.mxd"]
    
    # Need to make a list of the pdfs in the input folder, then
    # split it into 8 separate lists.
    
    inputFolderToUse = inputFolder1
    
    # List the pdfs here.
    inputFileList = os.listdir(inputFolderToUse)
    
    inputFileListCleaned = list()
    
    # Clean the list of non-pdf files.
    for inputFile1 in inputFileList:
        if inputFile1[-4:] == ".pdf":
            inputFileListCleaned.append(inputFile1)
            print "keeping: " + str(inputFile1)
        else:
            print "not keeping: " + str(inputFile1)
            pass
            #inputFileList.remove(inputFile1)
    
    startingTime = datetime.datetime.now()
    
    
    print "Starting Time: " + str(startingTime)
    
    pdfsToCompositeContainer = list()
    
    try:
        coreCount = mp.cpu_count()
    except:
        coreCount = 4
        
    splitNumber = coreCount + 2 # Test performance with this, and with + 2. If "+ 2" works better, consider "math.Ceil(coreCount * 1.5)"
    
    pdfsToCompositeList = list()
    
    for x in range(0, splitNumber):
        pdfsToCompositeList = list()
        fileCounter = 0
        for inputFile in inputFileListCleaned:
            if (fileCounter % splitNumber) == x:
                pdfsToCompositeList.append(inputFile)
            else:
                pass
            fileCounter += 1
        pdfsToCompositeContainer.append(pdfsToCompositeList)
    
    
    # Setup a list of processes that we want to run
    processes = [mp.Process(target=subProcessPDFCompositor, args=(inputFolderToUse, outputFolder1, pdfsToComposite)) for pdfsToComposite in pdfsToCompositeContainer]
    #old#processes = [mp.Process(target=exportMapPDFs, args=(outputQueue, countyMapSizeInfo, mapsLocation, outputLocation, targetMapName)) for targetMapName in mxdList]
    
    # Consider using pool.map_async(rand_string, mxdList). -- Figure out how to do this without pool also though.
     
    # Run processes
    for p in processes:
        p.start()
     
    # Exit the completed processes
    for p in processes:
        p.join()
    '''
    ###########################################
    # For the full script, need to add
    # the second input folder location here
    # also and rerun the multiprocessing
    # for that folder.
    # ^^ Added a mainProcess_ and changed
    # the subprocess name to subProcess_
    ########################################
    
    # Get process results from the output queue
    #results = [outputQueue.get() for p in processes]
    
    #for resultItem in results:
    #    print (resultItem + "\n " + 
    #    "Retrieved time: " + str(datetime.datetime.now()))
    
    
    endingTime = datetime.datetime.now()
    
    scriptDuration = FindDuration(endingTime, startingTime)
    
    print "\n" # Newline for better readability.
    print "For the main/complete script portion..."
    print "Starting Time: " + str(startingTime)
    print "Ending Time: " + str(endingTime)
    print "Elapsed Time: " + scriptDuration
    
    # Doesn't work well on dt00ar60. Wait for/ask again about getting a geoprocessing server
    # and try it there.
    
    '''
    listCounter1 = 0
    
    for pdfsToComposite in pdfsToCompositeContainer:
        print "List of PDFs #" + str(listCounter1) + ":"
        for pdfFile in pdfsToComposite:
            print str(pdfFile)
        listCounter1 += 1
    '''
    
else:
    pass

