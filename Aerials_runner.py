from MapDocument import MapDocument
from topos_utils import *
import arcpy
from photo import *
import sys
import logging

##################### logging ######################
#should logging go here or should it go in main?
# here is th place where i am trying out the logging
LOG_FILENAME = r'J:\GIS_Data\Working-MikeM\python_data\aerial_runner3.log'
# using __name__ makes it so the function name gets printed into the output log file
logger = logging.getLogger()
# we can set it here or have it be set from the outside on the command line
logger.setLevel(logging.DEBUG)
# add a handler for the file
handler = logging.FileHandler(LOG_FILENAME)
# message style is just like scotts but i am adding name
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# add the formatter to the handler
handler.setFormatter(formatter)
# and add the handler to logger
logger.addHandler(handler)
##################################################

COUNTYANDPROJECT = r'C:\HIGCore\HIGCore.gdb\CountyAndProjectImport'
COUNTYMOSAIC = r'C:\HIGCore\HIGCore.gdb\CountyMosaicImport'
DOQQ = r'C:\HIGCore\HIGCore.gdb\DOQQImport'
ArcMapDocument = r'J:\GIS_Data\Working-MikeM\python_data\AerialMerger.mxd'
LOOPER = (
          (COUNTYANDPROJECT, COUNTYPATTERN),
          (COUNTYMOSAIC, COUNTYMOSAICPATTERN),
          (DOQQ, DOQQPATTERN)
          )

def selectPhotos(orderNumber, outdir=r'C:\temp\topoCrops'):
    """"""
    md = MapDocument.createTopoMapDoc(orderNumber, logger=logger, scale=6000, height=9, width=8)
    poly = md.createArcPolygon()
    rasters = []
    for layer, pattern in LOOPER:
        layerrasters = [Photo(raster[0]) for raster in findRasters(poly, layer, relationship='contains')]
        for raster in layerrasters:
            raster.parseBaseName(pattern=pattern)
            outpath = os.path.join(outdir, raster.basename + '.tif')
            raster.clipByPoly(outpath, poly)
            if hasattr(raster, 'project'):
                print raster, raster.project
        rasters += layerrasters
    return rasters, md
        
def main():
    """"""
    orderNumber = '145187'# sys.argv[1]
    selectPhotos(orderNumber)

if __name__ == '__main__':
    main()

