#mike mommsen april 2014

#imports
import arcpy
import os
import sys

RASTERFORMATS = ['.tif', '.jp2', '.jpg', '.sid']#add more as they are needed - we could merge this list with the list from find world files.py

def clipByExtent(rawextent, inraster, outdir,rasterExtent=None):
    """takes a rawextent object (arcpy) and returns the portion of the raster that is in the exent"""
    # think about changing rawextent to a better name
    if not rasterExtent:
        rasterExtent = arcpy.Describe(inraster).extent
    # this line below seems to cause some problems with .sid files
    # it asks if the raster contains the clipping box
    if rasterExtent.contains(rawextent):
        # join together the extent to throw into the clipper
        extent = ' '.join(map(str,(rawextent.XMin, rawextent.YMin,rawextent.XMax, rawextent.YMax)))
        # this line below makes a different folder for each order or area
        # the structure of the output has not been static, so there will be changes here in the future
        outpath = outdir
        # take the tail of the raster, remove the extension and add .jpg to make the output name
        outname = os.path.splitext(os.path.split(inraster)[1])[0] + '.jpg'
        # if the ouput subfolder does not exist we make it
        if not os.path.exists(outpath):
            os.mkdir(outpath)
        # and now we finally do the clip
        outfile = arcpy.Clip_management(inraster,extent,os.path.join(outpath, outname), "#", "#", "NONE")
        return outfile
    else:
        print inraster, 'does not contain'
        return None

def clip_by_polyLayer(clipper, inraster, outdir):
    """takes a poly layer, loops through it and creates a clip of
    the image for each polygon in the clip layer named by the name field"""
    # start up a cursor to loop through the clipper feature
    cur = arcpy.SearchCursor(clipper)
    # grab the raster extent to compare with the extent of the clipping polygons
    desc = arcpy.Describe(inraster)
    rasterExtent = desc.extent
    # we do this inside a try clause in case there is a problem so we can still delete the cursor in a finally loop
    try:
        # loop through each row of the feature class
        for r in cur:
            # grab the name - this should maybe be paramaterized
            order = r.name
            # the geog column is usually SHAPE so grab the geog
            geog = r.getValue('SHAPE')
            # grab the extent of the geography
            rawextent = geog.extent
            # call the clipByExtent function
            clipResponse = clipByExtent(rawextent, inraster, rasterExtent=None):
    except Exception as e:
        print e
    # and finally always delete these to prevent any locking issues
    finally:
        del r, cur

def main():
    """"""
    # if there are at least 4 args (title included) then we can use them
    if len(sys.argv) >= 4:
        outdir = sys.argv[1]
        clipper = sys.argv[2] 
        inrasters = sys.argv[3:] 
    # if there are not enough args we can use some preset ones here
    else:
        print 'not enough args, using script set presets'
        inrasters = [r'C:\temp\topoCrops\2003.jpg']
        outdir = r'C:\temp\topoCrops\bulk'
        clipper = r'J:\GIS_Data\Working-MikeM\production\bulk_mpls\crop_boxes.shp'
    # if the output path does not exist then we need to make it
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    # inraster will always be a list because we are taking a slice
    # so that way we can loop through it
    for inraster in inrasters:
        # if one of the inrasters is a dir, we loop through all of the photos in that dir
        # i am unsure if this is the best behavior, and i have never done this up to this point
        if os.path.isdir(inraster):
            rasters = [x for x in os.listdir(inraster) if not os.path.isdir(x) and os.path.splitext(x)[1] in RASTERFORMATS]
            for raster in rasters:
                clip_by_polyLayer(clipper, raster, indir)
        # if it is not a dir that means we just call the clip function
        else:
            clip_by_polyLayer(clipper, inraster, indir)
            # print out raster name so people know whats up
            print inraster

if __name__ == '__main__':
    pass
    #main()
