# This script takes a polygon shapefile, and for each polygon feature creates
# an n by n grid of new polygons inside it that are equal in area. This new grid
# is created in a temporary scratch layer

# Notes for new users:
# -  The input layer must have an identifying metadata field called "GridID".
# -  Currently, the output layer will have a corresponding field "GridID", which
#    is simply <input feature GridID> + . + <integer between 1 and n>
# -  You must adjust the following inputs before running:
#    -  path_to_input_layer
#    -  input_layer

# Imports
from qgis.core import (
    QgsApplication,
    QgsDataSourceUri,
    QgsCategorizedSymbolRenderer,
    QgsClassificationRange,
    QgsPointXY,
    QgsProject,
    QgsExpression,
    QgsField,
    QgsFields,
    QgsFeature,
    QgsFeatureRequest,
    QgsFeatureRenderer,
    QgsGeometry,
    QgsGraduatedSymbolRenderer,
    QgsMarkerSymbol,
    QgsMessageLog,
    QgsRectangle,
    QgsRendererCategory,
    QgsRendererRange,
    QgsSymbol,
    QgsVectorDataProvider,
    QgsVectorLayer,
    QgsVectorFileWriter,
    QgsWkbTypes,
    QgsSpatialIndex,
    QgsVectorLayerUtils,
)

# Inputs
path_to_input_layer = "C:\\foo\\bar\\...\\VectorData\\"
input_layer = QgsVectorLayer(path_to_input_layer + "InputLayer.shp", "InputLayer", "ogr")
input_features = input_layer.getFeatures()

sides = 4

# Outputs
output_layer = QgsVectorLayer("Polygon?crs=epsg:22391", "OutputLayer", "memory")   #make a scratch layer so there is no risk of overwriting a file accidentally
output_fields = input_layer.fields()

output_layer.dataProvider().addAttributes(output_fields)    #add same fields to output layer's data provider as are in input layer
output_layer.updateFields()                                 #after adding data to the provider, the layer must be updated manually

# Functions
def extent_point_in_position(extents: list, vert: str, horz: str):
    """
    Returns the point whose coordinates correspond to the given vertical and horizontal descriptions
    
    Extents must be a list of nested [x,y] lists
    """
    # Sort points into ascending order of y values
    extents.sort(key=lambda point: point[1])     #on lambda keyword, see https://dbader.org/blog/python-min-max-and-nested-lists#fn:2
    
    if vert == "bottom":
        bottom_points = [extents[0], extents[1]]         #the two points with the lowest y values
        bottom_points.sort(key=lambda point: point[0])   #points are now in ascending order of x values
        
        if horz == "left":
            return bottom_points[0]
        elif horz == "right":
            return bottom_points[1]
        
    elif vert == "top":
        top_points = [extents[-2], extents[-1]]         #the two points with the highest y values
        top_points.sort(key=lambda point: point[0])     #points are now in ascending order of x values
        
        if horz == "left":
            return top_points[0]
        elif horz == "right":
            return top_points[1]
        
    else:
        print("Error: input directions must be top, bottom, left, or right\nExiting...")
        return


def small_grid_point(extents: list, n, i, k):
    """
    Calculates the position of a point in the given row and column with the given extents
    
    Extents must be a list of nested [x,y] lists
    """    
    # Check for too many extents
    if len(extents) != 4:
        print("Error: extents must be a list of 4 points!\nExiting...")
        return
    
    # separate extents list into the correct order
    A = extent_point_in_position(extents, "bottom", "left")
    B = extent_point_in_position(extents, "top", "left")
    C = extent_point_in_position(extents, "top", "right")
    D = extent_point_in_position(extents, "bottom", "right")
    
    # Calculate x and y coordinates
    x = (((n-i)*(n-k)/n)*A[0] + ((i)*(n-k)/n)*B[0] + ((i)*(k)/n)*C[0] + ((n-i)*(k)/n)*D[0])/n
    y = (((n-i)*(n-k)/n)*A[1] + ((i)*(n-k)/n)*B[1] + ((i)*(k)/n)*C[1] + ((n-i)*(k)/n)*D[1])/n
    return [x, y]

def create_small_rectangle(extents: list,  attribute1, value1, attribute2, value2, layer):
    """
    Makes a small rectangle in the given layer with the given extents
    
    extents must be a list of nested [x,y] lists
    attribute is the name of the attribute that will be used to identify the output feature
    value is the value to assign to the output feature's identifying attribute
    """
    #Re-format extents into a list of GqsPoint objects
    extents = [QgsPointXY(x,y) for x,y in extents]
    
    #Create a new feature containing a polygon with the given extents
    feature = QgsFeature()
    feature.setGeometry(QgsGeometry.fromPolygonXY([extents])) #ref: https://gis.stackexchange.com/questions/86812/how-to-draw-polygons-from-the-python-console/86901

    #Set the new feature's attributes
    feature.setFields(layer.fields())             #enables fields to be referenced by name in the setAttributes method below
    feature[attribute1] = value1                    #can also use output_feature.setAttribute(attribute, value)
    feature[attribute2] = value2
    
    #Update the data file and add the updated data to the QGIS project
    layer.dataProvider().addFeatures([feature])     #add output feature to layer's data provider
    layer.updateExtents()                           #update layer extents based on the new info in the data provider
    QgsProject.instance().addMapLayers([layer])     #add updated layer to the qgis project instance
    return

# Make list of grid point indices (this will be used for each
indices = [[i,k] for i in range(sides+1) for k in range(sides+1)] #indices that will be used to create the small grid points (this could be more elegant if I used numpy)

# Make small grid in each big grid rectangle
for input_feature in input_features:
    #Print the name of the current big grid square
    print("Creating small grid in " + input_feature.attribute("GridID"))
    
    #Get info for the current big grid rectangle
    input_feature_name = input_feature.attribute("GridID")
    input_geom = input_feature.geometry().asMultiPolygon()
    input_feature_extents = [[point.x(),point.y()] for point in input_geom[0][0]]   #unwrap the QgsPoint objects (unclear why input_geom is several nested lists)
    input_feature_extents = input_feature_extents[:-1]                              #remove the last point, which is always a duplicate
    
    #Calculate the locations of the small grid vertices
    small_grid_points = [small_grid_point(extents=input_feature_extents, n=sides, i=i, k=k) for i,k in indices]
    
    #Create small grid rectangles
    for i in range(sides):      #iterate over rows
        for k in range(sides):  #iterate over columns
            #Determine ID of current rectangle
            rect_num = i*(sides)+k+1
            grid_id = input_feature_name + "." + str(rect_num)   #full id of the current rectangle
            print("Creating small grid rectangle " + grid_id)
            
            #Get the points for the current rectangle (this could be more elegant)
            p1 = small_grid_points[i*(sides+1)+k]
            p2 = small_grid_points[(i+1)*(sides+1)+k]
            p3 = small_grid_points[(i+1)*(sides+1)+(k+1)]
            p4 = small_grid_points[(i)*(sides+1)+(k+1)]
            output_feature_extents = [p1, p2, p3, p4]
            
            #Make the current rectangle
            create_small_rectangle(extents=output_feature_extents, attribute1="GridID", value1=grid_id, attribute2="id", value2=rect_num, layer=output_layer)
            
            print("Finished with " + input_feature_name)

print("Small grid completed!")
    
    
    