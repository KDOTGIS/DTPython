#!/usr/bin/env python
# -*- coding: utf-8 -*-
# loggingusageexample.py
# Created: 2015-01-30

import datetime
import sys
from arcpy import env, GetMessages, ListFeatureClasses, ListFields
from supportfunctions import FindDuration, SCRIPT_FAILURE, SCRIPT_SUCCESS, ScriptStatusLogging  # @UnresolvedImport


startingTime = datetime.datetime.now()

gdbLocation = r'C:\GIS\Geodatabases\ExampleGDB.gdb'
env.workspace = gdbLocation
env.overwriteOutput = True

def exampleFunction():
    try:
        featureClassList = ListFeatureClasses()
        if len(featureClassList) > 0:
            for featureClassItem in featureClassList:
                fieldList = ListFields(featureClassItem)
                print str(featureClassItem) + " includes the following fields:"
                for fieldItem in fieldList:
                    print str(fieldItem.name)
        else:
            print "No feature classes found at this level. Maybe they're inside a feature dataset?"
            
    except:
        errorMessages = str(sys.exc_info()[1]) + str(GetMessages(2))
        errorMessages = ' '.join(errorMessages.split()) # This removes newlines.
        errorMessages = errorMessages[:255] # Truncate the error message so that it's short enough to be inserted.
        print "The following error has occurred and will be logged: " + errorMessages
        ScriptStatusLogging('loggingusageexample.py', 'ExampleGDB.gdb', SCRIPT_FAILURE, startingTime, datetime.datetime.now(), errorMessages)
        raise # Reraises the previous exception. This statement is optional.
        # The unhandled exception will cause the script to terminate. This is desirable in some cases, but not in others.


if __name__ == "__main__":
    exampleFunction()
    
    endingTime = datetime.datetime.now()
    scriptDuration = FindDuration(endingTime, startingTime)
    print 'The script completed successfully in ' + str(scriptDuration)
    
    try:
        ScriptStatusLogging('loggingusageexample.py', 'ExampleGDB.gdb',
                            SCRIPT_SUCCESS, startingTime,
                            endingTime, 'Completed Successfully')
    except:
        print "The script completed, but nothing was written to the log."