import sys
import os
import arcpy

def getcorners(inPoint, mapwidth, mapheight, scale):
    """"""
    surfacewidth = mapwidth * scale
    surfaceheight = mapheight * scale
    nw = inPoint.X, inPoint.Y
    ne = inPoint.X, inPoint.Y
    se = inPoint.X, inPoint.Y
    sw = inPoint.X, inPoint.Y

def main():
    arg1 = sys.argv[1]
    arg2 = sys.argv[2]

if __name__ == '__main__':
    main()
