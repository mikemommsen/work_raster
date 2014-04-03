import os
import sys
from PIL import Image

def copyRasterToJpeg(inraster, outraster):
    """takes a infile (tested with tif) and copys it into the outlocation as a jpeg (.jpg) using PIL"""
    img = Image.open(inraster).convert('RGB')
    img.save(outraster)

def main():
    # takes two directories. the first is the indir which should have a bunch of photos in it
    # the second is the outdir, which is where the jpgs are placed
    # if there are files that are in the outdir they will not be overwritten the way that it is currently written
    if len(sys.argv) == 3:
        indir = sys.argv[1]
        outdir = sys.argv[2]
    else:
        print 'using script presets because not right amount of args'
        indir = r'\\Works1\f\USGS\SWAX'
        outdir = r'C:\Workspace\georeferencing\test_swax'
    rasters = os.listdir(indir)
    for raster in rasters:
        inraster = os.path.join(indir, raster)
        outraster = os.path.join(outdir, os.path.splitext(raster)[0]) + '.jpg'
        if not os.path.exists(outraster):
            copyRasterToJpeg(inraster, outraster)

if __name__ == '__main__':
    main()
