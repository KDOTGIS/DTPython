'''
Created on Feb 10, 2015
@author: kyleg
DAT - 2015-04-24 Changed gdb target  for testing.
DAT - 2015-05-07 Modified to work with ArcMap Parameter input.
DAT - 2015-05-11 Modified to accept Locator Name and choice of KDOT/Non-KDOT fields.
# //TODO: Test with KDOT/Non-KDOT field choices for full code paths.
'''

try:
    from NG911_Config import currentPathSettings
except:
    "Go ahead, debug this in ArcMap... but you will have to copy and paste the NG911_Config file first"
import os
import re
from arcpy import (CreateAddressLocator_geocoding, Describe, Delete_management, env, Exists, GetParameterAsText)
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement, parse


#crashdata = r"Database Connections\KCARSPRD.sde\KCARS.ACCIDENTS_TO_GEO"
Roads = "RoadCenterline"
Alias = "RoadAlias"


def UpdateOptionsWithParameters(optionsObject):
    try:
        option0 = GetParameterAsText(0)
        option1 = GetParameterAsText(1)
        option2 = GetParameterAsText(2)
    except:
        pass
    
    if (option0 is not None and option0 != ""):
        optionsObject.gdbPath = option0
    else:
        pass
    if (option1 is not None and option1 != ""): # Name of the Address Locator
        optionsObject.locatorName = option1
    else:
        optionsObject.locatorName = "KCARS_Crash_Loc"
    if (option2 is not None and option2 != ""): # Boolean choice of whether or not to use KDOT fields
        optionsObject.useKDOTFields = option2
    else:
        pass
    
    return optionsObject


def CreateCrashLocator(optionsObject):
    # Make this in a folder so that you can modify the .loc file
    # to set the correct settings prior to the initial geocode.
    
    gdb = optionsObject.gdbPath
    
    outAddressLocator = optionsObject.locatorName
    
    roadChecksTestResult = None
    
    # Get the gdb_name and then remove "RoadChecks.gdb" from it, if it exists,
    # if not, just remove .gdb, then call it gdb_name + KCARS_Crash_Loc
    ## Replaced previous matching code with a Regex version.
    roadChecksPattern = re.compile(r'_RoadChecks\.gdb', re.IGNORECASE)
    
    roadChecksTestResult = re.search(roadChecksPattern, gdb)
    
    if roadChecksTestResult is not None:
        pass
    else:
        gdb = str(gdb[:-4])
        gdb = gdb + "_RoadChecks.gdb"
    
    gdbDesc = Describe(gdb)
    gdbPath = gdbDesc.Path
    gdbBasename = gdbDesc.Basename
    gdbName = gdbDesc.Name
    gdbExts = gdbDesc.Extension
    
    print gdbPath
    
    env.workspace = gdbPath
    locatorRemovalBase = os.path.join(gdbPath, outAddressLocator)
    
    try:
        os.remove(locatorRemovalBase + ".loc")
        os.remove(locatorRemovalBase + ".loc.xml")
        os.remove(locatorRemovalBase + ".lox")
    except OSError:
        pass
    
    #create the geocoding address locator service that works the best for locating crashes from KCARS data
    inReferenceRoads = gdb + "\\NG911\\RoadCenterline 'Primary Table';"
    inReferenceAlias = gdb + "\\RoadAlias 'Alternate Name Table'"
    inReferenceData = inReferenceRoads + inReferenceAlias
    #in_field_map="'Primary Table:Feature ID' RoadCenterline:SEGID VISIBLE NONE;'*Primary Table:From Left' RoadCenterline:L_F_ADD VISIBLE NONE;'*Primary Table:To Left' RoadCenterline:L_T_ADD VISIBLE NONE;'*Primary Table:From Right' RoadCenterline:R_F_ADD VISIBLE NONE;'*Primary Table:To Right' RoadCenterline:R_T_ADD VISIBLE NONE;'Primary Table:Prefix Direction' RoadCenterline:PRD VISIBLE NONE;'Primary Table:Prefix Type' RoadCenterline:STP VISIBLE NONE;'*Primary Table:Street Name' RoadCenterline:RD VISIBLE NONE;'Primary Table:Suffix Type' RoadCenterline:STS VISIBLE NONE;'Primary Table:Suffix Direction' RoadCenterline:POD VISIBLE NONE;'Primary Table:Left City or Place' RoadCenterline:KDOT_CITY_L VISIBLE NONE;'Primary Table:Right City or Place' RoadCenterline:KDOT_CITY_R VISIBLE NONE;'Primary Table:Left ZIP Code' RoadCenterline:KDOT_COUNTY_L VISIBLE NONE;'Primary Table:Right ZIP Code' RoadCenterline:KDOT_COUNTY_R VISIBLE NONE;'Primary Table:Left State' <None> VISIBLE NONE;'Primary Table:Right State' <None> VISIBLE NONE;'Primary Table:Left Street ID' <None> VISIBLE NONE;'Primary Table:Right Street ID' <None> VISIBLE NONE;'Primary Table:Display X' <None> VISIBLE NONE;'Primary Table:Display Y' <None> VISIBLE NONE;'Primary Table:Min X value for extent' <None> VISIBLE NONE;'Primary Table:Max X value for extent' <None> VISIBLE NONE;'Primary Table:Min Y value for extent' <None> VISIBLE NONE;'Primary Table:Max Y value for extent' <None> VISIBLE NONE;'Primary Table:Left Additional Field' <None> VISIBLE NONE;'Primary Table:Right Additional Field' <None> VISIBLE NONE;'Primary Table:Altname JoinID' <None> VISIBLE NONE;'*Alias Table:Alias' RoadAlias:SEGID VISIBLE NONE;'*Alias Table:Street' RoadAlias:KDOT_ROUTENAME VISIBLE NONE;'Alias Table:City' '' VISIBLE NONE;'Alias Table:State' <None> VISIBLE NONE;'Alias Table:ZIP' <None> VISIBLE NONE"
    inFieldMap="'Primary Table:Feature ID' RoadCenterline:SEGID VISIBLE NONE;'*Primary Table:From Left' RoadCenterline:L_F_ADD VISIBLE NONE;'*Primary Table:To Left' RoadCenterline:L_T_ADD VISIBLE NONE;'*Primary Table:From Right' RoadCenterline:R_F_ADD VISIBLE NONE;'*Primary Table:To Right' RoadCenterline:R_T_ADD VISIBLE NONE;'Primary Table:Prefix Direction' RoadCenterline:PRD VISIBLE NONE;'Primary Table:Prefix Type' RoadCenterline:STP VISIBLE NONE;'*Primary Table:Street Name' RoadCenterline:RD VISIBLE NONE;'Primary Table:Suffix Type' RoadCenterline:STS VISIBLE NONE;'Primary Table:Suffix Direction' RoadCenterline:POD VISIBLE NONE;'Primary Table:Left City or Place' RoadCenterline:KDOT_CITY_L VISIBLE NONE;'Primary Table:Right City or Place' RoadCenterline:KDOT_CITY_R VISIBLE NONE;'Primary Table:Left ZIP Code' RoadCenterline:KDOT_COUNTY_L VISIBLE NONE;'Primary Table:Right ZIP Code' RoadCenterline:KDOT_COUNTY_R VISIBLE NONE;'Primary Table:Left State' <None> VISIBLE NONE;'Primary Table:Right State' <None> VISIBLE NONE;'Primary Table:Left Street ID' <None> VISIBLE NONE;'Primary Table:Right Street ID' <None> VISIBLE NONE;'Primary Table:Display X' <None> VISIBLE NONE;'Primary Table:Display Y' <None> VISIBLE NONE;'Primary Table:Min X value for extent' <None> VISIBLE NONE;'Primary Table:Max X value for extent' <None> VISIBLE NONE;'Primary Table:Min Y value for extent' <None> VISIBLE NONE;'Primary Table:Max Y value for extent' <None> VISIBLE NONE;'Primary Table:Left Additional Field' <None> VISIBLE NONE;'Primary Table:Right Additional Field' <None> VISIBLE NONE;'Primary Table:Altname JoinID' RoadCenterline:SEGID VISIBLE NONE;'*Alternate Name Table:JoinID' RoadAlias:SEGID VISIBLE NONE;'Alternate Name Table:Prefix Direction' RoadAlias:A_PRD VISIBLE NONE;'Alternate Name Table:Prefix Type' RoadAlias:A_STP VISIBLE NONE;'Alternate Name Table:Street Name' RoadAlias:KDOT_ROUTENAME VISIBLE NONE;'Alternate Name Table:Suffix Type' RoadAlias:A_STS VISIBLE NONE;'Alternate Name Table:Suffix Direction' RoadAlias:A_POD VISIBLE NONE"
    
    #CreateAddressLocator_geocoding("US Address - Dual Ranges", in_reference_data, in_field_map, out_address_locator, config_keyword="", enable_suggestions="DISABLED")
    CreateAddressLocator_geocoding("US Address - Dual Ranges", inReferenceData, inFieldMap, outAddressLocator, config_keyword="", enable_suggestions="DISABLED")
    UpdateCrashLocatorProperties(gdbPath, outAddressLocator, optionsObject.useKDOTFields)


def UpdateCrashLocatorProperties(workspacePath, locatorName, useKDOTIntersect):
    # This is the part where you will have to open the address locator.loc
    # file and then append 
    
    intersectFieldName = ""
    
    ## Seems to work better than testing with is True.
    if str(useKDOTIntersect).lower() == "true".lower(): 
        intersectFieldName = "ON_AT_ROAD_KDOT_INTERSECT"
    else:
        ## This should already exist in the target data.
        intersectFieldName = "ON_AT_ROAD_INTERSECT"
    
    locatorPath = os.path.join(workspacePath, locatorName)
    locatorPath = locatorPath + ".loc"
    
    dataToAppend = """
Interpolate.SideValue.Left = L
Interpolate.SideValue.Right = R

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;  Esri Geocoder Misc Optional Properties
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

IntersectionConnectors = |
MinimumMatchScore = 65
MinimumCandidateScore = 25
EndOffset = 3
SideOffset = 20
SideOffsetUnits = Feet
SpellingSensitivity = 50
MatchIfScoresTie = true
WriteXYCoordFields = false
WriteStandardizedAddressField = false
WriteReferenceIDField = true
WritePercentAlongField = false
BatchPresortCacheSize = 50000

BatchPresortInputs = State
BatchPresortInputs = ZIP
BatchPresortInputs = City

EndOffsetUnits = Percent
MaxCandidates = 200
MaxPerfectCandidates = 200
NumThreads = 1
RuntimeMemoryLimit = 511705088
SearchTimeout = 1
ShowElapsedTime = false
StorageSegmentSizeKB = 128
StoreStandardizedRefData = true
WriteAdditionalOutputFields = true
WriteDispXDispYFields = false
WriteDisplayExtentFields = false
WriteLocatorSpecificFields = false
reportScorePerComponent = false
supportsEmptyHouseNumber = false
supportsHouseNoUnit = true
supportsIntersections = true
supportsOptionalZone = false
supportsSubAddress = false
supportsWeightedHouseNumber = true

"""
    try:
        openedFile = open(locatorPath, 'a')
        
        dataLinesList = dataToAppend.splitlines()
        print "Data To Append: "
        for dataLine in dataLinesList:
            print dataLine
            openedFile.write(dataLine + "\n")
        
        pass
    except IOError:
        print "There was an IOError."
    finally:
        openedFile.close()
        print "File Closed."
    
    print "Function complete."
    
    ## Try reading in the .loc.xml document
    ## Then, try finding the area where you need
    ## to add the first resource, then
    ## try adding the first resource
    ## and saving the file.
    ## ^^ Done.
    ## Then, try using the geocoder.
    ## ^^ Successfully geocoded points with the geocoder. (1141/2351)
    ## ^^ Then successfully offset from the geocoded points. (996/1141) (996/2351 overall)
    
    try:
        locatorXMLPath = locatorPath + ".xml"
        tree = parse(locatorXMLPath)
        root = tree.getroot()
        locatorList = root.findall('locator')
        locatorItem = locatorList[0]
        print locatorItem
        
        inputsList = locatorItem.findall('inputs')
        
        inputsItem = inputsList[0]
        print inputsItem
        
        inputSingularList = inputsItem.findall('input')
        
        for inputSingularItem in inputSingularList:
            print inputSingularItem
            
            if inputSingularItem.attrib["name"].lower() == str("Street").lower():
                print "Found the \"Street\" named input."
                # Add to the element.
                elemToAppend = Element('recognized_name')
                elemToAppend.text = intersectFieldName
                inputSingularItem.append(elemToAppend)
            elif inputSingularItem.attrib["name"].lower() == str("City").lower():
                print "Found the \"City\" named input."
                # Add to the element.
                elemToAppend = Element('recognized_name')
                elemToAppend.text = "CITY_NBR"
                inputSingularItem.append(elemToAppend)
            elif inputSingularItem.attrib["name"].lower() == str("ZIP").lower():
                print "Found the \"ZIP\" named input."
                # Add to the element.
                elemToAppend = Element('recognized_name')
                elemToAppend.text = "COUNTY_NBR"
                inputSingularItem.append(elemToAppend)
            else:
                pass
                
            inputResourceList = inputSingularItem.findall('recognized_name')
            for inputResource in inputResourceList:
                print inputResource.text
        
        tree.write(locatorXMLPath)
    
    except:
        pass
    
    finally:
        try:
            del tree
        except:
            pass
    
    try:
        # Add the doctype declaration string back in.
        xmlFile = open(locatorXMLPath, 'r')
        
        xmlContentsList = xmlFile.readlines()
        
        xmlFile.close()
        
    except IOError:
        pass
    
    finally:
        del xmlFile
    
    try:
        # Insert the doctype as the first item in the list.
        xmlContentsList.insert(0, '<?xml version="1.0" encoding="UTF-8"?>\n')
        
        # Reopen the file for writing.
        xmlFile = open(locatorXMLPath, 'w')
        
        xmlFile.writelines(xmlContentsList)
        
        xmlFile.close()
        
    except IOError:
        pass
    
    finally:
        del xmlFile


def CreateCrashLocator_OLD(gdb):
    #create the geocoding address locator service that works the best for locating crashes from KCARS data
    from arcpy import CreateAddressLocator_geocoding
    in_reference_roads=gdb+"\\NG911\\RoadCenterline 'Primary Table';"
    in_reference_alias = gdb+"\\RoadAlias 'Alternate Name Table'"
    in_reference_data = in_reference_roads+in_reference_alias
    #in_field_map="'Primary Table:Feature ID' RoadCenterline:SEGID VISIBLE NONE;'*Primary Table:From Left' RoadCenterline:L_F_ADD VISIBLE NONE;'*Primary Table:To Left' RoadCenterline:L_T_ADD VISIBLE NONE;'*Primary Table:From Right' RoadCenterline:R_F_ADD VISIBLE NONE;'*Primary Table:To Right' RoadCenterline:R_T_ADD VISIBLE NONE;'Primary Table:Prefix Direction' RoadCenterline:PRD VISIBLE NONE;'Primary Table:Prefix Type' RoadCenterline:STP VISIBLE NONE;'*Primary Table:Street Name' RoadCenterline:RD VISIBLE NONE;'Primary Table:Suffix Type' RoadCenterline:STS VISIBLE NONE;'Primary Table:Suffix Direction' RoadCenterline:POD VISIBLE NONE;'Primary Table:Left City or Place' RoadCenterline:KDOT_CITY_L VISIBLE NONE;'Primary Table:Right City or Place' RoadCenterline:KDOT_CITY_R VISIBLE NONE;'Primary Table:Left ZIP Code' RoadCenterline:KDOT_COUNTY_L VISIBLE NONE;'Primary Table:Right ZIP Code' RoadCenterline:KDOT_COUNTY_R VISIBLE NONE;'Primary Table:Left State' <None> VISIBLE NONE;'Primary Table:Right State' <None> VISIBLE NONE;'Primary Table:Left Street ID' <None> VISIBLE NONE;'Primary Table:Right Street ID' <None> VISIBLE NONE;'Primary Table:Display X' <None> VISIBLE NONE;'Primary Table:Display Y' <None> VISIBLE NONE;'Primary Table:Min X value for extent' <None> VISIBLE NONE;'Primary Table:Max X value for extent' <None> VISIBLE NONE;'Primary Table:Min Y value for extent' <None> VISIBLE NONE;'Primary Table:Max Y value for extent' <None> VISIBLE NONE;'Primary Table:Left Additional Field' <None> VISIBLE NONE;'Primary Table:Right Additional Field' <None> VISIBLE NONE;'Primary Table:Altname JoinID' <None> VISIBLE NONE;'*Alias Table:Alias' RoadAlias:SEGID VISIBLE NONE;'*Alias Table:Street' RoadAlias:KDOT_ROUTENAME VISIBLE NONE;'Alias Table:City' '' VISIBLE NONE;'Alias Table:State' <None> VISIBLE NONE;'Alias Table:ZIP' <None> VISIBLE NONE"
    in_field_map="'Primary Table:Feature ID' RoadCenterline:SEGID VISIBLE NONE;'*Primary Table:From Left' RoadCenterline:L_F_ADD VISIBLE NONE;'*Primary Table:To Left' RoadCenterline:L_T_ADD VISIBLE NONE;'*Primary Table:From Right' RoadCenterline:R_F_ADD VISIBLE NONE;'*Primary Table:To Right' RoadCenterline:R_T_ADD VISIBLE NONE;'Primary Table:Prefix Direction' RoadCenterline:PRD VISIBLE NONE;'Primary Table:Prefix Type' RoadCenterline:STP VISIBLE NONE;'*Primary Table:Street Name' RoadCenterline:RD VISIBLE NONE;'Primary Table:Suffix Type' RoadCenterline:STS VISIBLE NONE;'Primary Table:Suffix Direction' RoadCenterline:POD VISIBLE NONE;'Primary Table:Left City or Place' RoadCenterline:KDOT_CITY_L VISIBLE NONE;'Primary Table:Right City or Place' RoadCenterline:KDOT_CITY_R VISIBLE NONE;'Primary Table:Left ZIP Code' RoadCenterline:KDOT_COUNTY_L VISIBLE NONE;'Primary Table:Right ZIP Code' RoadCenterline:KDOT_COUNTY_R VISIBLE NONE;'Primary Table:Left State' <None> VISIBLE NONE;'Primary Table:Right State' <None> VISIBLE NONE;'Primary Table:Left Street ID' <None> VISIBLE NONE;'Primary Table:Right Street ID' <None> VISIBLE NONE;'Primary Table:Display X' <None> VISIBLE NONE;'Primary Table:Display Y' <None> VISIBLE NONE;'Primary Table:Min X value for extent' <None> VISIBLE NONE;'Primary Table:Max X value for extent' <None> VISIBLE NONE;'Primary Table:Min Y value for extent' <None> VISIBLE NONE;'Primary Table:Max Y value for extent' <None> VISIBLE NONE;'Primary Table:Left Additional Field' <None> VISIBLE NONE;'Primary Table:Right Additional Field' <None> VISIBLE NONE;'Primary Table:Altname JoinID' RoadCenterline:SEGID VISIBLE NONE;'*Alternate Name Table:JoinID' RoadAlias:SEGID VISIBLE NONE;'Alternate Name Table:Prefix Direction' RoadAlias:A_PRD VISIBLE NONE;'Alternate Name Table:Prefix Type' RoadAlias:A_STP VISIBLE NONE;'Alternate Name Table:Street Name' RoadAlias:KDOT_ROUTENAME VISIBLE NONE;'Alternate Name Table:Suffix Type' RoadAlias:A_STS VISIBLE NONE;'Alternate Name Table:Suffix Direction' RoadAlias:A_POD VISIBLE NONE"
    out_address_locator=gdb+"\\KCARS_Crash_Loc"
    #CreateAddressLocator_geocoding("US Address - Dual Ranges", in_reference_data, in_field_map, out_address_locator, config_keyword="", enable_suggestions="DISABLED")
    CreateAddressLocator_geocoding("US Address - Dual Ranges", in_reference_data, in_field_map, out_address_locator, config_keyword="", enable_suggestions="DISABLED")


if __name__ == '__main__':
    currentPathSettings = UpdateOptionsWithParameters(currentPathSettings)
    
    CreateCrashLocator(currentPathSettings)
    
else:
    pass