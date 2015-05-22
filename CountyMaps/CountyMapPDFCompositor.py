#!/usr/bin/env python
# -*- coding: utf-8 -*-
# CountyMapPDFCompositor.py

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

print "Imports complete."

# Make a function, then call it with both input folders.

inputFolder1 = r"\\gis\planning\Cart\Maps\MXD\2014_Update\quarterInch"
outputFolder1 = r"\\gis\planning\Cart\Maps\MXD\2014_Update\quarterInch\Composited"

inputFolder2 = r"\\gis\planning\Cart\Maps\MXD\2014_Update\halfInch"
outputFolder2 = r"\\gis\planning\Cart\Maps\MXD\2014_Update\halfInch\Composited"

def compositePDFs(inputFolderToComposite, outputFolderForComposites):
    
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
    
    
    for inputFile1 in inputFileListCleaned:
        compositeValue = 1
        
        print inputFile1
        inputPath1 = os.path.join(inputFolderToComposite, inputFile1)
        
        outputPath1 = os.path.join(outputFolderForComposites, (inputFile1[:-4] + "Composited.pdf"))
        
        print ("Compositor input = " + inputPath1)
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
                
                print("Writing " + outputPath1)
                outputStream = file(outputPath1, "wb")
                outputWriter.write(outputStream)
                print("Done writing"  + outputPath1)
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
        
    print "\nCompositing complete for " + str(inputFolderToComposite) + "!"

# For some reason, this code ran much faster for the half inch versions than it did for the quarter inch
# versions. Is rotating/merging the pdf an additional time really that expensive of an operation?

# Might have to do with symbology changes in CountyMapHalf18x24V as opposed to the smaller maps, esp.
# given that it should have the majority of the maps in the folder which are not 36 inch on a side.

# Could also have to do with the data source changes there -- it's possible that the
# geometry from the layers in SDEDEV draws cleaner in PDF, even though it seems to result in
# a larger file size. -- Will need to reexport all of the other PDFs with this new layer set
# and symbology anyways.


# TODO: Remember to update the other PDFs with the new layers and data sources. Also, remember to
# change the legend entries/make three column for the maps that can handle it. Might need to do
# something different on the 9x12 maps. Not sure if they will allow for a 3 column legend, but
# there is not much space to spare vertically either. Could be a problem.

# Also look at the difference in filesize & process time between maps that are created as PDFs with
# the different Vectorize/Rasterize options. These maps might benefit greatly from having
# the text converted to Raster. However, this runs the risk of causing the text to be difficult to
# see when printed, so it will probably be wise to do a test print of each of those options, all
# using the same map.

# Preferably, will use a triple-composited map for each test -- a 9x12 that
# requires rotation for compositing would be a good candidate since that should give
# the longest possible composite time and the most chance for quality degradation.
# ^ Should test on the map type with the most potential for problems. That way
# if there are no problems, there should* be less chance for errors on the other
# maps than had I tested on a simpler map, such as a 24x36.


# Well, need to figure out how to add multiprocessing to this anyways. An obvious choice would simply
# be to add multiprocessing at the folder level, but since it seems that the halfInch Version finishes much faster, there
# is probably a better way to do it. Maybe creating a list of all the files in the folder in the leader
# process and passing subdivided lists to the worker processes.

# Instead, might consider building a list of all the files in the quarter inch folder first,
# then, splitting that into 8 or so chunks and compositing those.

# Then, complete those processes and build a list of all the files in the half inch folder second.
# Next, split that list into 8 or so chunks again and composite those.

# Don't forget to make that part of the script a function that can be called from main. Also
# change the capitalization of the script so that it is easier to fork/spawn as a multiprocess
# since capitalization from calling the script absolutely matters when it comes to
# trying to spawn a new process... which is unfortunate as it makes things somewhat less readable.

# Could maybe move to using underscores or similar. Definitely need to make shorter names, however.
# Might start abbreviating things just a bit instead of spelling things out as I have been doing.

# Could call things cm_* instead of CountyMap* or CountyMaps* - Would make it easier to keep the.
# naming consistent then as well as there would be no problem with plurality consistency.

# Find a good way of splitting lists into multiple lists. For instance, is it better to
# take the 2nd element of every list as a new list, then do that over and over
# until you're happy with the total list size of each list, or is there
# a more effective way that will still work on variable length lists?

# Given that there should be 105 maps of each type, maybe variable length lists are not
# so much of a concern for this particular implementation, though.

# Changed away from: --
# Changed to: Convert Mark Symbols to Polygons.

if __name__ == "__main__":
    compositePDFs(inputFolder1, outputFolder1)
    compositePDFs(inputFolder2, outputFolder2)
    print "Script complete."


## Next script: CountyMapDataDrivenPagesToPDF.py