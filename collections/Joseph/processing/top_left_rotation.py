from qgis.core import *
from qgis.gui import *
import math

@qgsfunction(args='auto', group='Custom')
def top_left_rotation(feature, parent):
    """
    Calculates the angle of the top-left line of a rectangular polygon
    """
    def extent_point_in_position(horz, vert, feature):
        """
        Returns the point whose coordinates correspond to the given vertical and horizontal descriptions
        """
        # Convert geometry into a list of points in simple [x,y] form
        geom = feature.geometry().asPolygon()
        extents = [[point.x(),point.y()] for point in geom[0]]   #unwrap the QgsPoint objects (unclear why geom is several nested lists)
        
        # Sort points into ascending order of x values
        extents.sort(key=lambda point: point[0])     #on lambda keyword, see https://dbader.org/blog/python-min-max-and-nested-lists#fn:2
        
        if horz == "left":
            left_points = [extents[0], extents[1]]         #the two points with the lowest x values
            left_points.sort(key=lambda point: point[1])   #order points by ascending y values
            
            if vert == "bottom":
                return left_points[0]
            elif vert == "top":
                return left_points[1]
            
        elif horz == "right":
            right_points = [extents[-2], extents[-1]]         #the two points with the highest x values
            right_points.sort(key=lambda point: point[1])     #order points by ascending y values
            
            if vert == "bottom":
                return right_points[0]
            elif vert == "top":
                return right_points[1]
    
    # Get top left and right points
    p1 = extent_point_in_position("left", "top", feature)
    p2 = extent_point_in_position("right", "top", feature)
    
    # Find angle
    angle = (-1) * math.atan((p2[1] - p1[1]) / (p2[0] - p1[0]))
    return math.degrees(angle)