#mike mommsen april 2014

#imports
import arcpy
import os
import sys

RASTERFORMATS = ['.tif', '.jp2', '.jpg', '.sid']#add more as they are needed - we could merge this list with the list from find world files.py

def clip_by_polyLayer(clipper, inraster, outdir):
    """takes a poly layer, loops through it and creates a clip of
    the image for each polygon in the clip layer named by the name field"""
    cur = arcpy.SearchCursor(clipper)
    xlist, ylist = [], []
    desc = arcpy.Describe(inraster)
    rasterExtent = desc.extent
    try:
        for r in cur:
            order = r.name #os.path.split(inraster)[1]
            geog = r.getValue('SHAPE')
            rawextent = geog.extent
            if rasterExtent.contains(rawextent):
                extent = ' '.join(map(str,(rawextent.XMin, rawextent.YMin,rawextent.XMax, rawextent.YMax)))
                outpath = os.path.join(outdir, order)
                outname = os.path.splitext(os.path.split(inraster)[1])[0] + '.jp2'
                if not os.path.exists(outpath):
                    os.mkdir(outpath)
                arcpy.Clip_management(inraster,extent,os.path.join(outpath, outname), "#", "#", "NONE")
            else:
                print rasterExtent
                print rawextent
    except Exception as e:
        print e
    finally:
        del r, cur

if not os.path.exists(outdir):
    os.mkdir(outdir)


newlist = [r'H:\Mosaics\2008\MN_NAIP08\ortho_1-1_1m_j_mn053_2008_3.jp2']

for i in newlist:
    clip_by_polyLayer(clipper, i, outdir)

def main():
    """"""
    if len(sys.argv) == 4:
        inraster = sys.argv[1] #r'C:\temp\topoCrops\2003.jpg'
        outdir = sys.argv[1] #r'C:\temp\topoCrops\bulk'
        clipper = sys.argv[1] #r'J:\GIS_Data\Working-MikeM\production\bulk_mpls\crop_boxes.shp'
    else:
        print 'not the right amount of args, using script set presets'
        inraster = r'C:\temp\topoCrops\2003.jpg'
        outdir = r'C:\temp\topoCrops\bulk'
        clipper = r'J:\GIS_Data\Working-MikeM\production\bulk_mpls\crop_boxes.shp'
    if os.path.isdir(inraster):
        rasters = [x for x in os.listdir(inraster) if not os.path.isdir(x) and os.path.splitext(x)[1] in RASTERFORMATS]

if __name__ == '__main__':
    pass
    #main()
