import sys
import os
import arcpy

class LinearScale:
    """"""
    def __init__(self, domain=[0,1], outrange=[0,1], limit=False):
        """"""
        self.domain = domain
        self.domainExtent = domain[1] - domain[0]
        self.outrangeExtent = outrange[1] - outrange[0]
        self.outrange = outrange
        self.limitDomain = limitDomain
        self.limitOutRange = limitOutRange
    
    def get(inval):
        """"""
        if limit:
            assert domain[0] < inval < domain[1], 'needs to be inside the domain when limit is set to true'
            

def getcorners(inPoint, mapwidth, mapheight, scale):
    """takes the upper left corner and returns a polygon """
    array = arcpy.array
    pnt = arcpy.Point()
    surfacewidth = mapwidth * scale
    surfaceheight = mapheight * scale
    nw = inPoint.X, inPoint.Y
    ne = inPoint.X - surfacewidth, inPoint.Y
    se = inPoint.X - surfacewidth, inPoint.Y - surfaceheight
    sw = inPoint.X, inPoint.Y - surfaceheight
    return [nw, ne, se, sw]

def main():
    arg1 = sys.argv[1]
    arg2 = sys.argv[2]

if __name__ == '__main__':
    main()
