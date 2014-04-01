import sys
import os
import arcpy

INCHESPERMETER = 39.3701
INCHESPERFOOT = 12

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
        indiff = float(inval - self.domain[0])
        inz = indiff / self.domainExtent
        outz = inz * self.outrangeExtent
        outval = outz + self.outrange[0]
        return outval
        
    def invert(self):
        """"""
        return LinearScale(self.outrange, self.domain, self.limit)
        
class Domain:
    """"""
    def __init__(self, name, low, high, limit):
        """"""
        self.name = name
        self.low = low
        self.high = high
        self.limit = limit
        
    def __str__(self):
        basetext =  'Domain object named {name} with low val: {low}, high val: {high}, and limit:{limit}'
        return basetext.format(self.__dict__)
        
class ManyWayLinearScale:
    """"""
    def __init__(self, **kwargs):
        """"""
        
        
        
        
class ScaleTwoDimensions(object):
    """"""
    def __init__(self, domainX=[0,1], domainY=[0,1], outrangeX=[0,1], outrangeY=[0,1], limit=False):
        """"""
        self.scaleX = LinearScale(domainX, outrangeX, limit)
        self.scaleY = LinearScale(domainY, outrangeY, limit)
        
    def get(self, invalX, invalY):
        """"""
        x = self.scaleX.get(invalX)
        y = self.scaleY.get(invalY)
        return (x, y)
        
    def invert(self):
        """"""
        return ScaleTwoDimensions(self.domainY, self.domainX, self.outrangeY, self.outrangeX, self.limit)
        
class Corners:
    """"""
    def __init__(self, 
        
        
class MapDocument(ScaleTwoDimensions):
    """"""
    def __init__(self, width=8, height=9, scale=6000, corner=[0,0], cornertype='NW', spatialRef):
        self.width = width
        self.height = height
        self.scale = scale
        meterscale = scale / INCHESPERMETER
        self.meterwidth = meterwidth = width * meterscale
        self.meterheight = meterheight = height * meterscale
        # this section allows corner changing - maybe seperate function that is called by __init__
        if cornertype[0] ==  'N':
            pass
        elif cornertype[0] == 'S':
            corner[0] -= meterwidth
        elif cornertype[0] == 'C':
            corner[0] -= (meterwidth / 2)
        else:
            print 'unrecognized cornertype'
        if cornertype[1] ==  'W':
            pass
        elif cornertype[1] == 'E':
            corner[1] -= meterheight
        elif cornertype[1] == 'C':
            corner[1] -= (meterheight / 2)
        else:
            print 'unrecognized cornertype'
        # section ends here
        rightedge = x[0]
        topedge = x[1]
        leftedge = x[0] + meterwidth
        bottomedge = x[1] - meterheight
        self.corners = OrderedDict([('nw', nwCorner), ('ne', [topedge,leftedge]),
                                    ('se': [bottomedge,leftedge]), ('sw': [bottomedge,rightedge])])
        self.centroid = (nwCorner [0] - meterwidth, nwCorner[1] - meterheight)
        super(self.__class__, self).__init__(width, height, [nwCorner[0],leftedge],[nwCorner[1], bottomedge])# look up the syntax for this shit - its pretty cool though
        
    def createArcPolygon(self):
        """"""
        ar = arcpy.Array
        pnt = arcpy.Point
        for corner in self.corners.values():
            pnt.X = corner[0]
            pnt.Y = corner[1]
            ar.append(pnt)
        poly = arcpy.Poly(ar, self.spatialRef)
        
        
        
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
