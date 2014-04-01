import arcpy
import os

inraster = r'C:\temp\topoCrops\2003.jpg'
outdir = r'C:\temp\topoCrops\bulk'
clipper = r'J:\GIS_Data\Working-MikeM\production\bulk_mpls\crop_boxes.shp'

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
    pass

if __name__ == '__main__':
    pass
    #main()
