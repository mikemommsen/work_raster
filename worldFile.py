import sys
import os
#import arcpy
import geojson, json

# make sure that we import WORLD_FILES and read_metadata
WORLD_FILES = ['.jgw', '.jgwx', '.tfw', '.tfwx']
import read_metadata

def createPolygonGeojson(incoordinates, utmzone, outfile):
    crs = {'type': 'EPSG', 'properties': {'code': 26900 + utmzone}}
    poly = geojson.Polygon()
    poly.coordinates=incoordinates
    poly.crs = crs
    if outfile:
        with open(outfile, 'w') as f:
            json.dump(poly, f)
    else:
        return json.dumps(poly, indent=4)
    
def createPolygon(incoordinates, spref):
    """takes lat lon incoordinates and returns an arcpy polygon"""
    arrayObj = arcpy.Array()
    pnt = arcpy.Point()
    for lat, lon in incoordinates:
        pnt.X, pnt.Y = lon, lat
        arrayObj.add(pnt)
    poly = arcpy.Polygon(arrayObj, spref)
    return poly

def parseFolder(indir, outshapefile):
    """"""
    # this is close to working
    # just need to get the insert cursor to work appropriately
    # i would throw in a recursion option so that we can easily send any folder to it
    spref = arcpy.SpatialReference("NAD 1983 UTM Zone 17N")
    cur = arcpy.InsertCursor(outshapefile)
    os.chdir(indir)
    files = os.listdir('.')
    jpgs = [x for x in files if x[-4:] == '.jpg']
    for jpg in jpgs:
        basefilename, extension = os.path.splitext(jpg)
        supportFiles = [x for x in os.listdir('.') if x.split('.')[0] == basefilename]
        wf = findWorldFile(supportFiles)
        if wf:
            newrow = cur.newRow()
            wld = WorldFile(os.path.join(indir, jpg))
            corners = wld.getCorners()
            corners = [corners['NW'], corners['NE'],corners['SE'], corners['SW']]
            print corners
            poly = createPolygon(corners, spref)
            newrow.shape = poly
            newrow.Filename = os.path.join(indir, jpg)
            cur.insertRow(newrow)
            del newrow
    del cur

def parseFolderTree(indir, outshapefile):
    for a, b, c in os.walk(indir):
        mylist = (os.path.join(a,x) for x in b)
        for i in mylist:
            if os.path.isdir(i):
                parseFolder(i, outshapefile)
        

def findWorldFile(supportFiles):
    """"""
    worldFiles = [x for x in supportFiles if os.path.splitext(x)[1] in WORLD_FILES]
    if worldFiles:
        if len(worldFiles) == 1:
            return(worldFiles[0])
        xfiles = [x for x in worldFiles if 'x' in os.path.splitext(x)[1]]
        if xfiles and len(xfiles) == 1:
            return xfiles[0]

class WorldFile(object):
    """"""

    @classmethod
    def loadFromRasterPath(self, raster):
        """"""
        self.rasterpath = raster
        self.directory, self.filename = os.path.split(raster)
        self.basefilename, self.extension = os.path.splitext(self.filename)
        self.width, self.height = read_metadata.getsize(raster)
        self.supportFiles = [x for x in os.listdir(self.directory) if x.split('.')[0] == self.basefilename]
        self.worldfile = os.path.join(self.directory, findWorldFile(self.supportFiles))
        self.parseWorldFile()
        
    def parseWorldFile(self, worldfile=None):
        """"""
        if not worldfile:
            worldfile = self.worldfile
            with open(worldfile) as f:
                self.worldText = f.read()
        rows = self.worldText.split('\n')
        fields = ['ypixelsize', 'xrotation', 'yrotation', 'xpixelsize', 'yorigin', 'xorigin']
        for f, r in zip(fields, rows[:6]):
            setattr(self, f, float(r))
        
    def __init__(self, raster, wkid=None):
        """"""
        self.rasterpath = raster
        self.directory, self.filename = os.path.split(raster)
        self.basefilename, self.extension = os.path.splitext(self.filename)
        self.width, self.height = read_metadata.getsize(raster)
        self.supportFiles = [x for x in os.listdir(self.directory) if x.split('.')[0] == self.basefilename]
        self.worldfile = os.path.join(self.directory, findWorldFile(self.supportFiles))
        self.parseWorldFile()
            
    def __str__(self):
        """"""
        return '\n'.join([self.xpixelsize, self.xrotation, self.yrotation, self.ypixelsize, self.xorigin ,self.yorigin])
            
    def writeWorldFile(self, outfile):
        """"""
        # we could change this using the string function for worldFile
        fields = ['ypixelsize', 'xrotation', 'yrotation', 'xpixelsize', 'yorigin', 'xorigin']
        with open(outfile, 'w') as f:
            for field in fields:
                f.write(getattr(self, field))
            
    def getCoordinate(self, pixel, row):
        """"""
        x = self.xorigin + self.xpixelsize * pixel + self.xrotation * row
        y = self.yorigin + self.ypixelsize * row + self.yrotation * pixel
        return x, y
        
    def getPixel(self, x, y):
        """"""
        denom = self.xpixelsize * self.ypixelsize - self.yrotation * self.xrotation
        pixel = (self.ypixelsize * x - self.xrotation * y + self.xrotation * self.yorigin - self.ypixelsize * self.xorigin) / denom
        row = (-self.yrotation * x + self.xpixelsize * y + self.yrotation * self.xorigin - self.xpixelsize * self.yorigin) / denom
        return pixel, row
    
    def getCorners(self):
        """"""
        mydict = {'NW': self.getCoordinate(-.5,-.5),
                  'NE': self.getCoordinate(-.5,self.width-.5),
                  'SE': self.getCoordinate(self.height-.5, self.width-.5),
                  'SW': self.getCoordinate(self.height-.5, -.5)}
        return mydict
        
    @classmethod
    def createWorldFromCorners(cls, corners, raster):
        """"""
        from math import hypot
        fields = ['ypixelsize', 'xrotation', 'yrotation', 'xpixelsize', 'yorigin', 'xorigin']
        average = lambda indict, inkey1, inkey2: (x['utmLat' + inkey1] + x['utmLat' + inkey2]) / 2, (x['utmLon' + inkey1] + x['utmLon' + inkey2]) / 2
        distance = lambda x,y: hypot(x[0] - y[0], x[1] - y[1])
        skew = lambda x, y: (x[1] - y[1]) / (x[0] - y[0])
        leftmean = average(corners, 'NW', 'SW')
        rightmean = average(corners, 'NE', 'SE') 
        topmean = average(corners, 'NW', 'NE')
        bottommean = average(corners, 'SW', 'SE') 
        meterwidth = distance(leftmean, rightmean)
        meterheight = distance(topmean, bottomean)
        pixelcountwidth, pixelcountheight = read_metadata.getsize(raster)
        pixelwidth = meterwidth / pixelcountwidth
        pixelhieght =  meterheight / pixelcountheight
        skew1 = skew(bottommean, topmean)
        skew2 = skew(leftmean, rightmean)
        
        with open(raster.split('.')[0] + 'jgw') as f:
            f.write(self.worldText)
        return cls(raster)
        
def main():
    """"""
    pass
    
if __name__ == '__main__':
    main()

