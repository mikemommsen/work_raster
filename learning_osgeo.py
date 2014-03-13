# mike mommsen

from osgeo import gdal
from osgeo import ogr
from osgeo import osr
from osgeo import gdal_array
from osgeo import gdalconst


def createPolygon(incoordinates):
    """takes a list of coordinate pairs and returns an object"""
    # this seems unneeded when when you think of it
    
