#!/usr/bin/env python
# -*- coding: utf-8 -*-
# UseGeocoder.py
import os
from arcpy import env, Describe, GeocodeAddresses_geocoding, GetParameterAsText
from NG911_Config import currentPathSettings


# Is there any reason to use this when there is already a geocode_addresses tool?
def UpdateOptionsWithParameters(optionsObject):
    try:
        option0 = GetParameterAsText(0)
        option1 = GetParameterAsText(1)
        option2 = GetParameterAsText(2)
        option3 = GetParameterAsText(3)
        option4 = GetParameterAsText(4)
    except:
        pass
    
    if (option0 is not None): # Output location after offset (accidentDataWithOffsetOutput)
        optionsObject.gdbPath = option0
    else:
        pass
    if (option1 is not None): # Geocoded to Intersection (accidentDataAtIntersections)
        optionsObject.addressTable = option1
    else:
        pass
    if (option2 is not None): # Where the roads features are (roadsFeaturesLocation)
        optionsObject.addressLocator= option2
    else:
        pass
    if (option3 is not None): # Where the alias table for the roads features is (aliasTable)
        optionsObject.geocodeResult = option3
    else:
        pass
    
    if (option3 is not None): # Boolean choice of whether or not to use KDOT fields
        optionsObject.useKDOTFields = option4
    else:
        pass
    
    return optionsObject

# This function doesn't make any sense.
# It takes only a variable for gdb, but the in_table, address locator,
# and out feature class are likely to change also.
def GeocodeAddresses(gdb):
    #Perform the initial Geocode.
    GeocodeAddresses_geocoding(in_table="BARBER_004", address_locator=gdb+"\\KCARS_Crash_Loc3", in_address_fields="Street ON_AT_ROAD_INTERSECT VISIBLE NONE;City CITY_NBR VISIBLE NONE;ZIP COUNTY_NBR VISIBLE NONE", out_feature_class="Geocoding_Result1", out_relationship_type="STATIC")    

# Get parameters for:
env.workspace = "C:/ArcTutor/Geocoding/atlanta.gdb" 
# Set local variables:
address_table = "customers"
address_locator = "Atlanta_AddressLocator"
geocode_result = "geocode_result"

GeocodeAddresses_geocoding(address_table, address_locator, in_address_fields="Street ON_AT_ROAD_INTERSECT VISIBLE NONE;City CITY_NBR VISIBLE NONE;ZIP COUNTY_NBR VISIBLE NONE", geocode_result, out_relationship_type="STATIC")


if __name__ == "__main__":
    
    currentPathSettings = ChangeGdbPathViaParameter(currentPathSettings)
    
    ###############################################################################################
    # Setup for globals follows. Clean later and replace by passing an object.
    ###############################################################################################
    Originalgdb = currentPathSettings.gdbPath
    print Originalgdb
    Originalgdbdesc = Describe(Originalgdb)
    Originalgdbpath = Originalgdbdesc.Path
    Originalgdbbasename = Originalgdbdesc.Basename
    Originalgdbname = Originalgdbdesc.Name
    Originalgdbexts = Originalgdbdesc.Extension
    
    gdb = os.path.join(Originalgdbpath, Originalgdbbasename) + "_RoadChecks." + Originalgdbexts
    
    env.workspace = gdb
    
    GeocodeAddresses(gdb)
    
else:
    pass