import arcpy
import os
import sys

def process(toa, dem):
    #we need to
    # 1 project
    # 2 clip
    # 3 someother shit (mainly deleting some shit
    desc = arcpy.Describe(dem)
    spref = desc.spatialReference
    # is the extent an issue? this is only going to ive us the max mins not a real bounding box
    extent = desc.extent
    arcpy.ProjectRaster_management(dem, "reproject.tif", "World_Mercator.prj",\"BILINEAR", "5", "NAD_1983_To_WGS_1984_5", "#", "#")
    # make sure that we use a registration point to match the grids
    arcpy.Clip_management("image.tif",extent,"clip.gdb/clip", "#", "#", "NONE")



def main():
    pass
    
if __name__ == '__main__':
    main()

