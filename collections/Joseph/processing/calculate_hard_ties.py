# This script calculates expected hard-ties relative to True North for
# a set of specified features and a single specified reference point

from qgis.core import *
from qgis.gui import *
import math as m

def true_north_bearing(pointfeature, source_crs, project_instance):
    """
    Calculates the bearing (counter-clockwise) of True North relative to Grid 
    North at a specified point within a specified crs.
    """
    # Get feature geometry
    geom = pointfeature.geometry()
    
    # Define CRS transformation
    dest_crs = QgsCoordinateReferenceSystem(4326)
    tr = QgsCoordinateTransform(source_crs, dest_crs, project_instance)
    
    # Clone geometry and transform it
    geom2 = QgsGeometry(geom)
    geom2.transform(tr)
    
    # Shift the cloned geometry north along its meridian
    geom2.translate(0,0.001)
    
    # Transform Geometry back to source CRS
    tr = QgsCoordinateTransform(dest_crs, source_crs, project_instance)
    geom2.transform(tr)
    
    # Calculate angle between the two points
    p1 = geom.asPoint()
    p2 = geom2.asPoint()
    
    x1 = p1.x()
    y1 = p1.y()
    x2 = p2.x()
    y2 = p2.y()
    
    angle = QgsGeometryUtils.lineAngle(x1, y1, x2, y2)*(180/(m.pi))
    
    return angle
    
def measure_distance(feat1, feat2, project_instance):
    """
    Returns ellipsoidal distance between 2 point features in the project CRS.
    """
    # Configure the distance measurement
    proj_crs = project_instance.crs()
    distance = QgsDistanceArea()
    distance.setSourceCrs(proj_crs, project_instance.transformContext())
    distance.setEllipsoid(proj_crs.ellipsoidAcronym())
    
    # Measure distance
    geom1 = feat1.geometry()
    geom2 = feat2.geometry()
    p1 = geom1.asPoint()
    p2 = geom2.asPoint()
    m = distance.measureLine(p1, p2)
    
    return m
    
def calculate_hard_tie(ref_pt, ref_pt_name_field, feat_pt, project_instance):
    """
    Determines the distance and compass bearing (relative to True North) from
    a reference point to a feature point using the project CRS.
    
    Returns a string formatted as follows: '<distance> <unit> @ <bearing> deg
    from <ref_pt name>'
    """
    # Determine project CRS
    proj_crs = project_instance.crs()
    
    # Calculate distance to nearest cm
    distance = round(measure_distance(ref_pt, feat_pt, project_instance), 2)
    
    # Calculate bearing to nearest 0.1 degrees
    p1 = ref_pt.geometry().asPoint()
    p2 = feat_pt.geometry().asPoint()
    
    x1 = p1.x()
    y1 = p1.y()
    x2 = p2.x()
    y2 = p2.y()
    
    bearing_from_gn = QgsGeometryUtils.lineAngle(x1, y1, x2, y2)*(180/(m.pi))
    tn_bearing = true_north_bearing(feat_pt, proj_crs, project_instance)
    bearing_from_tn = round(bearing_from_gn + (360 - tn_bearing), 1)
    
    # Get Reference Point Name
    ref_pt_name = ref_pt[ref_pt_name_field]
    
    # Compose description
    description = f"{distance} m @ {bearing_from_tn} deg from {ref_pt_name}"
    
    return description

def create_hard_tie(from_pt, to_pt, desc,  from_text, to_text, layer, project_instance):
    """
    Create polyline feature representing a hard-tie
    """
    # Re-format the input features as QgsPoint objects
    from_pt = from_pt.geometry().asPoint()
    to_pt = to_pt.geometry().asPoint()
    
    #Create a new feature containing a polygon with the given extents
    feature = QgsFeature()
    feature.setGeometry(QgsGeometry.fromPolylineXY([from_pt, to_pt])) 
    
    #Set the new feature's attributes
    feature.setFields(layer.fields())
    feature.setAttribute("From", from_text)
    feature.setAttribute("Desc", desc)
    feature.setAttribute("To", to_text)
    
    #Update the data file and add the updated data to the QGIS project
    layer.dataProvider().addFeatures([feature])     #add output feature to layer's data provider
    layer.updateExtents()                           #update layer extents based on the new info in the data provider
    project_instance.addMapLayers([layer])     #add updated layer to the qgis project instance


# User inputs
feature_layer_name = "New scratch layer"
feature_id_field = "name"
reference_layer_name = "ReferencePoints"
reference_id_field = "RPID"

# Project variables
project_instance =  QgsProject.instance()
proj_crs = project_instance.crs()
proj_crs_code = str(proj_crs)[-10:-1]

# Get feature layer
feature_layer = project_instance.mapLayersByName(feature_layer_name)[0]
    
# Get features
print(f"Hard-ties will be determined for all features in '{feature_layer_name}'")
features = feature_layer.getFeatures()

# Get reference points
reference_layer = project_instance.mapLayersByName(reference_layer_name)[0]
ref_pt = ref_layer.selectedFeatures()[0]
ref_pt_name = ref_pt[reference_id_field]

# Create output layer
url = f"Linestring?crs={proj_crs_code}&field=To:string(100)&field=From:string(100)&field=Desc:string(200)"
output_layer = QgsVectorLayer(url, f"Hard-ties from {ref_pt_name}", "memory")

# Calculate hard-ties
for f in features:
    desc = calculate_hard_tie(ref_pt, ref_field, f, project_instance)
    from_text = ref_pt_name
    to_text = f[feature_id_field]
    create_hard_tie(ref_pt, f, desc, from_text, to_text, output_layer, project_instance)