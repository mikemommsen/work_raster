# mike mommsen
# june 2014
# import statements
import os
import sys

# these are all the imports for gdal shit
from osgeo import gdal
from osgeo import ogr
from osgeo import osr
from osgeo import gdal_array
from osgeo import gdalconst

def openImage(inimage):
    inDs = gdal.Open(inimage, GA_ReadOnly)
    return inimage
    
# open the image
def getSize(inimage):
    rows = inDs.RasterYSize
    cols = inDs.RasterXSize
    bands = inDs.RasterCount
    return rows, cols, bands

# get the bands and block sizes
inBand2 = inDs.GetRasterBand(2)
inBand3 = inDs.GetRasterBand(3)
blockSizes = inBand2.GetBlockSize()
xBlockSize = blockSizes[0]
yBlockSize = blockSizes[1]

def main():
    inphoto = sys.argv[1]

if __name__ == '__main__':
    main()
