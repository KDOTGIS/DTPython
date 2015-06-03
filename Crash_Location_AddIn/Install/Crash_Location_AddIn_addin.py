import pythonaddins
import time
import os

toolboxName = "Toolbox102"

# create a string with path to toolbox
toolboxPath = os.path.join(os.path.dirname(__file__), toolboxName + ".tbx")

class DataPrepNGfLRS(object):
    """Implementation for Crash_Location_Add-In_addin.button1 (Button)"""
 
    def __init__(self):
        self.enabled = True
        self.checked = False

    def onClick(self):
        # name of tool to be executed
        toolName = "NGfLRSScript"

        # call geoprocessing tool
        pythonaddins.GPToolDialog(toolboxPath, toolName)
        time.sleep(.2)


class BuildAccidentGeocoder(object):
    """Implementation for Crash_Location_Add-In_addin.button2 (Button)"""
    
    def __init__(self):
        self.enabled = True
        self.checked = False
    
    def onClick(self):
        # name of tool to be executed
        toolName = "MakeGeocoderScript"
        
        # call geoprocessing tool
        pythonaddins.GPToolDialog(toolboxPath, toolName)
        time.sleep(.2)


class FixRoadNameErrors(object):
    """Implementation for Crash_Location_Add-In_addin.button2 (Button)"""
    
    def __init__(self):
        self.enabled = True
        self.checked = False
    
    def onClick(self):
        # name of tool to be executed
        toolName = "FixRoadNamesScript"
        
        # call geoprocessing tool
        pythonaddins.GPToolDialog(toolboxPath, toolName)
        time.sleep(.2)


class UseAccidentGeocoder(object):
    """Implementation for Crash_Location_Add-In_addin.button3 (Button)"""
    
    def __init__(self):
        self.enabled = True
        self.checked = False
    
    def onClick(self):
        toolboxName = "Geocoding Tools"
        
        # name of tool to be executed
        toolName = "GeocodeAddresses"
        
        # call geoprocessing tool
        pythonaddins.GPToolDialog(toolboxName, toolName)
        time.sleep(.2)


class OffsetGeolocatedAccidents(object):
    """Implementation for Crash_Location_Add-In_addin.button4 (Button)"""
 
    def __init__(self):
        self.enabled = True
        self.checked = False

    def onClick(self):
        # name of tool to be executed
        toolName = "OffsetScript"

        # call geoprocessing tool
        pythonaddins.GPToolDialog(toolboxPath, toolName)
        time.sleep(.2)