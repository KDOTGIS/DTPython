#!/usr/bin/env python
# -*- coding: utf-8 -*-
# CCL_No_KDOT_Maint_Cities.py
# Created: 2014-11-24 @ 16:04:29PM
# Author: Dirk

# This script is meant to find out which cities do all of their own maintenance
# without any help from KDOT.

# Get a list of all the city-names using "if not in (citylist)" append to citylist.
# Then, do the same thing for city-names with KDOT Maintenance segments.
# Then, subtract the city-names with KDOT Maintenance from the
# list of all the city-names to get only the cities without any KDOT maintenance.

from arcpy import da
import os

resolutionCityList = list()
yesKDOTMaintCityList = list()
noKDOTMaintCityList = list()

sdeConn = r"C:\Users\dtalley\AppData\Roaming\ESRI\Desktop10.2\ArcCatalog\CCL_TEST.sde"
resolutionLayer = os.path.join(sdeConn, "CCL_TEST.DBO.CCL_Resolution")
maintenanceLayer = os.path.join(sdeConn, "CCL_TEST.DBO.Maint_Segment")

print "Getting all the city names with CCL Resolution Layer entries."
resolutionSearchCursor = da.SearchCursor(resolutionLayer, ["CITY"])
for row in resolutionSearchCursor: # -- Resolution layer searchCursor.
    tempCityName = str(row[0])
    tempCityName = tempCityName.upper()
    if tempCityName not in resolutionCityList:
        resolutionCityList.append(tempCityName)
    else:
        pass
        
print "Done getting all the city names with CCL Resolution Layer entries."

if "resolutionSearchCursor" in locals():
    del resolutionSearchCursor
else:
    pass

print "Getting all the city names with CCL KDOT Maintenance Layer entries."
maintSearchCursor = da.SearchCursor(maintenanceLayer, ["CITY_NAME"])
for row in maintSearchCursor: # -- Maintenance segment (KDOT) layer searchCursor.
    tempCityName = str(row[0])
    tempCityName = tempCityName.upper()   
    if tempCityName not in yesKDOTMaintCityList:
        yesKDOTMaintCityList.append(tempCityName)
    else:
        pass
print "Done getting the city names with CCL KDOT_Maintenance Layer entries."

if "maintSearchCursor" in locals():
    del maintSearchCursor
else:
    pass

print "Finding all the cities that have resolution segments, but no (KDOT) maintenance segments."
for cityNameItem in resolutionCityList:
    if str(cityNameItem) not in yesKDOTMaintCityList:
        noKDOTMaintCityList.append(str(cityNameItem))
    else:
        pass
print "Done finding the cities that do all their own maintenance."

print "There are " + str(len(noKDOTMaintCityList)) + " cities that do all of their own CCL maintenance."

for noKDOTMaintCity in sorted(noKDOTMaintCityList):
    print str(noKDOTMaintCity)