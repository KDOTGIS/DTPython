#!/usr/bin/env python
# -*- coding: utf-8 -*-
# supportfunctions.py
# Created: 2015-01-12
# Updated: 2015-01-30


""" Contains general support functions that can be
 imported into other scripts which contain
 functions for more specialized tasks. """


from arcpy import (da, env, GetMessages)  

import sys
import datetime
env.overwriteOutput = True
env.MResolution = 0.0001
env.MTolerance = 0.0002

# Changed scriptSuccess and scriptFailure to
# match the naming conventions for constants
# as SCRIPT_SUCCESS and SCRIPT_FAILURE

SCRIPT_SUCCESS = '0x0'
SCRIPT_FAILURE = '0x1'

def ScriptStatusLogging(taskName = 'Unavailable', taskTarget = 'Unknown',
                        completionStatus = SCRIPT_FAILURE, taskStartDateTime = datetime.datetime.now(), 
                        taskEndDateTime = datetime.datetime.now(), completionMessage = 'Unexpected Error.'):
    """Used to write information about python script completion/failure to a table for viewing later. Use this
     function to provide more detailed information about success/failure than the codes from task scheduler
     are able to provide on their own."""
    # Updated to run on SQL Server instead of Oracle.
    try:
        print 'Script status logging started.'
        
        # Calculate task duration and format it for insertion.
        # Duration should only be 00:00:00 when the information is
        # not correct.
        taskDuration = FindDuration(taskEndDateTime, taskStartDateTime)
        
        # Change the datetimes to ISO 8601 Format (YYYY-MM-DD HH:MM:SS).
        startTimeStamp = CreateTimeStamp(taskStartDateTime)
        
        endTimeStamp = CreateTimeStamp(taskEndDateTime)
        
        # Works well with SQL Server & FGDB tables.
        # Modifications may be required for other storage formats.
        processFC = r'C:\GIS\Geodatabases\PythonLog.gdb\scriptInformation' 
        processFieldList = ['Process_Name','Table_Name', 'Status', 'Start_Date', # Status 0x0 = Success, 0x1 = Failure.
                         'Completion_Date', 'Execution_Time', 'Process_Message']
        # Expects fields to be in the following formats:lengths.
        # The listed lengths are optional, just don't try to pass in more data than what you set them for.
        # Process_Name:Text:150
        # Table_Name:Text:100
        # Status:Text:25
        # Start_Date:Date
        # Completion_Date:Date
        # Execution_Time:Text:20
        # Process_Message:Text:255
        
        # Choose the logging table to write to based on the completion status.
        if completionStatus == SCRIPT_SUCCESS or completionStatus == SCRIPT_FAILURE: # Received the correct status format.
            
            # Create the row to be inserted and fill it with the proper values.
            newRow = [taskName, taskTarget, completionStatus, startTimeStamp, endTimeStamp, taskDuration, completionMessage]
            
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

def FindDuration(endTime, startTime):
    """Takes two datetime.datetime objects, subtracting the 2nd from the first
    to find the duration between the two."""
    duration = endTime - startTime
    
    dSeconds = int(duration.seconds)
    durationp1 = str(int(dSeconds // 3600)).zfill(2)
    durationp2 = str(int((dSeconds % 3600) // 60)).zfill(2)
    durationp3 = str(int(dSeconds % 60)).zfill(2)
    durationString = durationp1 + ':' +  durationp2 + ':' + durationp3
    
    return durationString

def CreateTimeStamp(inDateTime):
    """Takes a datetime.datetime object and returns
    the ISO 8601 Timestamp equivalent."""
    
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

if __name__ == "__main__":
    ScriptStatusLogging('supportfunctions.py', 'Status Test',
                        SCRIPT_SUCCESS, datetime.datetime.now(), 
                        datetime.datetime.now(), 'Script Success.')
    pass
else:
    pass