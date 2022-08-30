from qgis.core import *
from qgis.gui import *

@qgsfunction(args='auto', group='Custom')
def max_side_length(feature, parent):
    """
    Calculates the length of the longest side of a polygon (feature must be a polygon)
    """
    geom = feature.geometry().asMultiPolygon()
    points = geom[0][0]    #list of Qgspoint objects
    lengths = []        #list for the side lengths
    
    for i in range(len(points[:-1])):   #end the loop 1 point before the end
        p1 = points[i]
        p2 = points[i+1]
        
        lengths.append(p1.distance(p2))
    return max(lengths)