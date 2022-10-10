# Take an input layer, create a new field `UTM_Coord`, and populate it with
# UTM coordinates in the format `[utm zone] [easting] E, [northing] N`

# The input layer is the currently selected layer. This can be changed by 
# adjusting `layer` in line 103 below.

# Note that this script is currently configured to only use CSRS coordinate
# systems. This can be changed by adjusting `query` in line 91 below.

# Useful links:
#   https://www.geodose.com/2018/09/qgis-python-tutorial-add-field-attribute.html

from qgis.core import *
from qgis.gui import *
from PyQt5.QtCore import QVariant
import sqlite3

def find_latlong(output, feature, layer, project_instance):
    """
    Takes an input point geometry and returns a copy of it transformed to EPSG
    4326 as latitude and longitude coordinates
    Ref: https://gis.stackexchange.com/questions/349585/reprojecting-qgspointxy
    Ref: https://gis.stackexchange.com/questions/215550/getting-parent-layer-of-feature-in-qgis-pyqgis-custom-function
    Ref: https://github.com/qgis/QGIS/issues/41695
    """
    # Convert geometry into a point
    geom = feature.geometry()

    # Initialize crs and transformation instances
    source_crs = layer.sourceCrs()
    dest_crs = QgsCoordinateReferenceSystem(4326)
    tr = QgsCoordinateTransform(source_crs, dest_crs, project_instance)
    
    # clone geometry and transform it
    geom2 = QgsGeometry(geom)
    geom2.transform(tr)
    latlong = geom2.asPoint()
    
    # Return latitude and longitude as coordinates
    if output=='return_string':
        return str(latlong[0])+', '+str(latlong[1])
    elif output=='return_list':
        return [latlong[0], latlong[1]]
    elif output=='return_point':
        return latlong
    else:
        return 0

def latlong_to_utmzone(point):
    """Point x and y must be in degrees
    negative indicates W and S
    positive indicates E and N"""
    # Check that x and y are accepted
    if (point.x() < -180) or (point.x() > 180):
        return "Error: x out of range -180 to 180!"
    if point.y() < -80 or point.y() > 84:
        return "Error: y out of range -80 to 84!"

    # Determine Zone
    zones = [str(item).zfill(2) for item in range(1,61)]
    zone_index = int((point.x() + 180)/6)     #always rounds down
    zone = zones[zone_index]

    # Determine Band
    try:
        bands = ["C","D","E","F","G","H","J","K","L","M","N","P","Q","R","S","T","U","V","W","X"]
        band_index = int((point.y() + 80)/8)
        band = bands[band_index]
    except IndexError:
        band = "X"      #this band is 12 degrees instead of 8, and so could produce an index error

    return [zone,band]
    
def utmzone_to_crs_list(utmzone):
    """
    Returns a list of crs objects that match the given utm zone
    """
    #Split UTM zone into components
    zone = str(utmzone[0])
    band = utmzone[1]
    
    #Determine N or S hemisphere
    if band > 'M':
        hemi='N'
    else:
        hemi='S'

    # Query the SQLite DB and return the results
    con = sqlite3.connect(QgsApplication.srsDatabaseFilePath())
    cur = con.cursor()
    query = f"select * from vw_srs where description like 'NAD83%CSRS%UTM%"+zone+hemi+"' and deprecated is 0"
    print('performing sqlite query: '+query)
    cur.execute(query)
    rows = cur.fetchall()
    
    print('query results: '+str(rows))
    
    return rows


### Main code
# Inputs
layer = iface.activeLayer()
layer_provider = layer.dataProvider()
features = layer.getFeatures()
project_instance =  QgsProject.instance()
output_field_name= 'UTMCoord'

p = 1         #number of decimal places for the utm coordinates

# Check if layer has field 'UTMCoord', and if not then create the field
layer.startEditing()
field_names = layer.fields().names()

if output_field_name not in field_names:
    layer_provider.addAttributes([QgsField(output_field_name,QVariant.String)])
    layer.updateFields()

output_field_id = layer.fields().indexFromName(output_field_name)

# Process each feature
for f in features:
    # get feature id
    id = f.id()
    
    # Determine UTM zone and destination CRS
    latlong = find_latlong('return_point', f, layer, project_instance)
    utmzone = latlong_to_utmzone(latlong)
    utm_crs= utmzone_to_crs_list(utmzone)[0]   #just use the first result
    
    # Set transform settings
    source_crs = layer.sourceCrs()
    dest_crs = QgsCoordinateReferenceSystem('EPSG:'+str(utm_crs[6]))
    tr = QgsCoordinateTransform(source_crs, dest_crs, project_instance)
    print('transforming to EPSG: '+str(utm_crs[6]))
    
    # Copy the feature geometry and transoform it
    geom2 = QgsGeometry(f.geometry())
    geom2.transform(tr)
    
    # Construct the output string
    #   for help with string formatting, see these resources:
    #       https://stackoverflow.com/questions/15238120/keep-trailing-zeroes-in-python
    #       https://stackoverflow.com/questions/45310254/fixed-digits-after-decimal-with-f-strings
    point = geom2.asPoint()
    x = point.x()
    y = point.y()
    utm_coord =f"{utmzone[0]}{utmzone[1]} {x:#.{p}f} E {y:#.{p}f} N"
    
    # Update the feature's attribute value
    attr_value_dict = {output_field_id:utm_coord}
    layer_provider.changeAttributeValues({id:attr_value_dict})
    layer.commitChanges()
