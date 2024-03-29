# This script calculates expected hard-ties relative to True North for
# a set of specified features and a single specified reference point

# Usage:
#   1. In the layer that contains your reference points, select the feature you
#      want to use as the reference point for your hard-ties
#   2. In the code below, edit the following variables according to your needs:
#       - feat_layer_name   --> name of the layer with the features you want to
#                               calculate hard-ties to
#       - feat_id_field     --> name of the field with unique ids in your
#                               feature layer
#       - ref_layer_name    --> name of the layer with the reference points you
#                               want to calculate hard-ties to
#       - ref_id_field      --> name of the field with unique ids in your
#                               reference points layer

from qgis.core import *
from qgis.gui import *
import math as m

def true_north_bearing(pointfeature, source_crs, proj_inst):
    """
    Calculates the bearing (counter-clockwise) of True North relative to Grid 
    North at a specified point within a specified crs.
    """
    # Get feature geometry
    geom = pointfeature.geometry()
    
    # Define CRS transformation
    dest_crs = QgsCoordinateReferenceSystem(4326)
    tr = QgsCoordinateTransform(source_crs, dest_crs, proj_inst)
    
    # Clone geometry and transform it
    geom2 = QgsGeometry(geom)
    geom2.transform(tr)
    
    # Shift the cloned geometry north along its meridian
    geom2.translate(0,0.001)
    
    # Transform Geometry back to source CRS
    tr = QgsCoordinateTransform(dest_crs, source_crs, proj_inst)
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
    
def measure_distance(feat1, feat2, proj_inst):
    """
    Returns ellipsoidal distance between 2 point features in the project CRS.
    """
    # Configure the distance measurement
    proj_crs = proj_inst.crs()
    distance = QgsDistanceArea()
    distance.setSourceCrs(proj_crs, proj_inst.transformContext())
    distance.setEllipsoid(proj_crs.ellipsoidAcronym())
    
    # Measure distance
    geom1 = feat1.geometry()
    geom2 = feat2.geometry()
    p1 = geom1.asPoint()
    p2 = geom2.asPoint()
    m = distance.measureLine(p1, p2)
    
    return m
    
def calculate_hard_tie(ref_pt, ref_pt_name_field, feat_pt, proj_inst):
    """
    Determines the distance and compass bearing (relative to True North) from
    a reference point to a feature point using the project CRS.
    
    Returns a string formatted as follows: '<distance> <unit> @ <bearing> deg
    from <ref_pt name>'
    """
    # Determine project CRS
    proj_crs = proj_inst.crs()
    
    # Calculate distance to nearest cm
    distance = round(measure_distance(ref_pt, feat_pt, proj_inst), 2)
    
    # Calculate bearing to nearest 0.1 degrees
    p1 = ref_pt.geometry().asPoint()
    p2 = feat_pt.geometry().asPoint()
    
    x1 = p1.x()
    y1 = p1.y()
    x2 = p2.x()
    y2 = p2.y()
    
    bearing_from_gn = QgsGeometryUtils.lineAngle(x1, y1, x2, y2)*(180/(m.pi))
    tn_bearing = true_north_bearing(feat_pt, proj_crs, proj_inst)
    bearing_from_tn = round(bearing_from_gn + (360 - tn_bearing), 1)
    
    # Get Reference Point Name
    ref_pt_name = ref_pt[ref_pt_name_field]
    
    # Compose description
    description = f"{distance} m @ {bearing_from_tn} deg from {ref_pt_name}"
    
    return description

def create_hard_tie(from_pt, to_pt, desc,  from_txt, to_txt, layer, proj_inst):
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
    feature.setAttribute("From", from_txt)
    feature.setAttribute("Desc", desc)
    feature.setAttribute("To", to_txt)
    
    #Update the data file and add the updated data to the QGIS project
    layer.dataProvider().addFeatures([feature])     #add output feature to layer's data provider
    layer.updateExtents()                           #update layer extents based on the new info in the data provider
    proj_inst.addMapLayers([layer])     #add updated layer to the qgis project instance

def reproject_layer(layer, out_crs, proj_inst, add_to_iface=False):
    """
    Returns a copy of `layer` reprojected into `out_crs`
    If `add_to_iface` is True, also loads the reprojected layer into the active
    interface
    """
    # Input features
    in_feats = layer.getFeatures()
    
    # Initialize transformation
    t = QgsCoordinateTransform(layer.crs(), out_crs, proj_inst)
    
    # Initialize output layer
    geomtype = QgsWkbTypes.displayString(layer.wkbType())
    uri = geomtype+'?crs='+proj_inst.crs().authid()
    name = layer.name()+'_reprojected'
    layer_rpj = QgsVectorLayer(uri, name, 'memory')
    out_feats = []
    
    # Copy fields over
    layer_rpj.dataProvider().addAttributes(layer.fields())
    layer_rpj.updateFields()

    # Reproject
    for f in in_feats:
        geom = f.geometry()
        geom.transform(t)
        f.setGeometry(geom)
        out_feats.append(f)
    
    layer_rpj.dataProvider().addFeatures(out_feats)
    
    if add_to_iface:
        proj_inst.addMapLayer(layer_rpj, addToLegend=True)
    
    return layer_rpj

# User inputs
feat_layer_name = "New scratch layer"
feat_id_field = "name"
ref_layer_name = "ReferencePoints2"
ref_id_field = "RPID"

# Project variables
proj_inst =  QgsProject.instance()
proj_crs = proj_inst.crs()
proj_crs_code = str(proj_crs)[-10:-1]

# Get feature layer
feature_layer = proj_inst.mapLayersByName(feat_layer_name)[0]

# Get reference point layer
reference_layer = proj_inst.mapLayersByName(ref_layer_name)[0]

# Make sure feature and reference point layers are in the project CRS
# (reproject if necessary)
if reference_layer.crs() != proj_crs:
    print("Warning: reference point layer not in project crs. Reprojecting and continuing...")
    select_id = reference_layer.selectedFeatures()[0][ref_id_field]
    reference_layer = reproject_layer(reference_layer, proj_crs, proj_inst)
    reference_layer.selectByExpression(f"\"{ref_id_field}\" = '{select_id}'")

if feature_layer.crs() != proj_crs:
    print("Warning: feature layer not in project crs. Reprojecting and continuing...")
    feature_layer = reproject_layer(feature_layer, proj_crs, proj_inst)

# Get features
print(f"Hard-ties will be determined for all features in '{feature_layer_name}'")
features = feature_layer.getFeatures()

# Get reference points
ref_pt = reference_layer.selectedFeatures()[0]
ref_pt_name = ref_pt[ref_id_field]

# Create output layer
url = f"Linestring?crs={proj_crs_code}&field=To:string(100)&field=From:string(100)&field=Desc:string(200)"
output_layer = QgsVectorLayer(url, f"Hard-ties from {ref_pt_name}", "memory")

# Calculate hard-ties
for f in features:
    desc = calculate_hard_tie(ref_pt, ref_id_field, f, proj_inst)
    from_txt = ref_pt_name
    to_txt = f[feat_id_field]
    create_hard_tie(ref_pt, f, desc, from_txt, to_txt, output_layer, proj_inst)