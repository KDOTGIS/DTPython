# Turn_Off_Map_Layers.py
# Turn off visibility for the slower layers in a map that's not loading.
# -- Should make it load faster.
'''
Created on 2014-08-14
@author: Dirk
updated 2014-09-04 by Dirk
'''

from arcpy import RefreshTOC, RefreshActiveView
from arcpy.mapping import MapDocument, ListDataFrames, ListLayers, RemoveLayer
import os

#mapDocName = r'\\gisdata\ArcGIS\GISdata\MXD\2014090401_CCL_TESTing.mxd'
mapDocName = r'C:\GIS\MXD\2014090401_CCL_TESTing.mxd' # Try local file copy instead.

mxd = MapDocument(mapDocName)
df = ListDataFrames(mxd)[0]

layers = ListLayers(mxd, "K*", df) # Use K* to include the KDOR/Tax_Units group layer.

print layers

for layer in layers:
  if hasattr(layer, 'visible'):
    layer.visible = False
  else:
    pass

del layers
    
layers = ListLayers(mxd, "B*", df) # Use B* to include the background layer.

print layers

for layer in layers:
  if hasattr(layer, 'visible'):
    layer.visible = False
  else:
    pass

del layers

layers = ListLayers(mxd, "World*", df) # Use World* to include the World_Imagery layer.

print layers

for layer in layers:
  if hasattr(layer, 'visible'):
    layer.visible = False
  else:
    pass

del layers

layers = ListLayers(mxd, "CCL_REPORT*", df) # Try to remove the CCL_REPORT table.

for layer in layers:
  try:
    RemoveLayer(df, layer)
  except:
    pass
    
RefreshTOC()
RefreshActiveView()

mxd.save()

del mxd

exit()