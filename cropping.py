import sys
import os
import arcpy

class LinearScale:
    """"""
    def __init__(self, domain=[0,1], outrange=[0,1], limit=False):
        """"""
        if type(domain) == int:
            domain = [0, domain]
        if type(outrange) == int:
            outrange = [0, outrange]
        self.domain = domain
        self.outrange = outrange
        self.domainExtent = domain[1] - domain[0]
        self.outrangeExtent = outrange[1] - outrange[0]
        self.limit = limit
    
    def get(self, inval):
        """"""
        if self.limit:
            assert self.domain[0] < inval < self.domain[1], 'needs to be inside the domain when limit is set to true'
        indiff = inval - self.domain[0]
        inz = indiff / self.domainExtent
        outz = inz * self.outrangeExtent
        outval = outz + self.outrange[0]
        return outval
        
            

def polyFromPoint(inPoint, mapwidth, mapheight, scale):
    """takes the upper left corner and returns a polygon """
    array = arcpy.array
    pnt = arcpy.Point()
    surfacewidth = mapwidth * scale
    surfaceheight = mapheight * scale
    nw = inPoint.X, inPoint.Y
    ne = inPoint.X - surfacewidth, inPoint.Y
    se = inPoint.X - surfacewidth, inPoint.Y - surfaceheight
    sw = inPoint.X, inPoint.Y - surfaceheight
    poly = arcpy.Polygon(array([nw, ne, se, sw])) # make sure that we get the SRID in here, or whatever arc wants
    return poly
    
def changeCorners(inPoint, mapwidth, mapheight, scale, inPointCorner, outPointCorner):
    """"""
    surfacewidth = mapwidth * scale
    surfaceheight = mapheight * scale
    if inPointCorner == 'C':
        
    elif inPointCorner == 'NW':
        
    elif inPointCorner == 'NE':
    
    elif inPointCorner == 'SE':
        
    elif inPointCorner == 'SW':
    
        

def main():
    arg1 = sys.argv[1]
    arg2 = sys.argv[2]

if __name__ == '__main__':
    main()
