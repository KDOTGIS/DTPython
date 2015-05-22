#!/usr/bin/env python
# -*- coding: utf-8 -*-
# multiprocessingtest.py

import datetime


from arcpy import env, GetCount_management
from arcpy.da import SearchCursor as daSearchCursor  # @UnresolvedImport
import multiprocessing as mp
import random
import string

gdb = r'\\gisdata\ArcGIS\GISdata\GDB\CountyMappingDataMulti.gdb'

env.workspace = gdb

# Define an output queue
outputQueue = mp.Queue()

mxdList = ["9x12H.mxd", "9x12V.mxd", "12x18H.mxd", "12x18V.mxd", "18x24H.mxd", "18x24V.mxd", "24x36H.mxd", "24x36V.mxd"]

# incorporate the datetime.datetime.now() function to
# test the start time on these processes.
# define a example function
def rand_string(resultsOutputQueue, xCount):
    """ Generates a random string of numbers, lower- and uppercase chars. """
    rand_str = ''.join(random.choice(
                    string.ascii_lowercase 
                    + string.ascii_uppercase 
                    + string.digits)
               for i in range(xCount))
    
    countedNumber = GetCount_management('Counties_No_Z')
    #output.put(rand_str + str(countedNumber))
    
    startTime = str(datetime.datetime.now())
    
    xCount = str(xCount)
    
    randomNumber = random.randint(1, 105)
    searchCursorWhereClause = "\"COUNTY_NUMBER\" = " + str(randomNumber) + " "
    
    newCursor = daSearchCursor('Counties_No_Z', ["COUNTY_NAME", "COUNTY_NUMBER", "SHAPE@"], searchCursorWhereClause)
    
    for rowItem in newCursor:
        rowItemString = "Cursor Row Item: " + str(rowItem[0]) + " & " + str(int(rowItem[1])) + "."
        
    endTime = str(datetime.datetime.now())
    
    resultsOutputQueue.put("Process number: " + xCount + "\n " + 
               "Started: " + startTime + " \n " + 
               "Ended: " + str(datetime.datetime.now()) + "\n " +
               rand_str + " " + str(countedNumber) + " " + str(rowItemString))
    
    if "newCursor" in locals():
        del newCursor
    else:
        pass

# Try to write output to \\dt00mh71\planning\cart\maps\mxd\2014_update\multiprocessingTest
# into the halfInch and quarterInch directories.

# County number comes across as a float in str(rowItem[1]) -- not sure if this will cause
# any issues, but be aware of it.
 
if __name__ == "__main__":
    # try setting up a list of the maps
    # then, call a process for each map.
    
    # Setup a list of processes that we want to run
    processes = [mp.Process(target=rand_string, args=(outputQueue, x)) for x in mxdList]
    
    # Consider using pool.map_async(rand_string, mxdList). -- Figure out how to do this without pool also though.
     
    # Run processes
    for p in processes:
        p.start()
     
    # Exit the completed processes
    for p in processes:
        p.join()
     
    # Get process results from the output queue
    results = [outputQueue.get() for p in processes]
    
    for resultItem in results:
        print (resultItem + "\n " + 
        "Retrieved time: " + str(datetime.datetime.now()))
    
    #print(results)

else:
    pass