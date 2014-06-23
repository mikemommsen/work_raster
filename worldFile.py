import sys
import os

# make sure that we import WORLD_FILES and read_metadata
from read_metadata import WORLD_FILES

def findWorldFile(supportFiles):
    """"""
    worldFiles = [x for x in self.supportFiles if os.path.splitext(x)[1] in WORLD_FILES]
    if worldFiles:
        if len(worldFiles) == 1:
            return(worldFiles[0])
        xfiles = [x for x in worldFiles if 'x' in os.path.splitext(x)[1]]
        if xfiles and len(xfiles) == 1:
            return xfiles[0]

class WorldFile(Object):
    """"""
    @classmethod
    def loadFromRasterPath(cls, raster):
        cls.rasterpath = raster
        cls.directory, cls.filename = os.path.split(raster)
        cls.basefilename = os.path.splitext(cls.filename)
        cls.width, cls.height = read_metadata.getSize(raster)
        cls.supportFiles = [x for x in os.listdir(self.directory) if x.split('.')[0] == basefilename]
        cls.findWorldFile(supportFiles)
        return cls
        
    @classmethod
    def parseWorldFile(cls, worldFile):
        """"""
        with open(os.path.join(self.directory, self.worldFile)) as f:
            self.worldText = f.read
        rows = self.worldText.split('\n')
        
        return cls(*rows)
        
    def __init__(self, xpixelsize, xrotation, yrotation, ypixelsize, xorigin, yorigin, width=None, height=None, wkid=None):
        """"""
        self.xpixelsize = xpixelsize
        self.xrotation = xrotation
        self.yrotation = yrotation
        self.ypixelsize = ypixelsize
        self.xorigin = xorigin
        self.yorigin = yorigin
        self.width = width
        self.height = height
        self.wkid = wkid
            
    def __str__(self):
        """"""
        return '\n'.join(self.xpixelsize, self.xrotation, self.yrotation, self.ypixelsize, self.xorigin ,self.yorigin)
            
    def writeWorldFile(self, outfile):
        """"""
        # we could change this using the string function for worldFile
        fields = ['xpixelsize', 'xrotation', 'yrotation', 'ypixelsize', 'xorigin', 'yorigin']
        with open(outfile, 'w') as f:
            for field in fields:
                f.write(getattr(self, field))
            
    def getCoordinate(self, pixel, row):
        """"""
        x = self.xorigin + self.xpixelsize * pixel + self.yrotation * row
        y = self.yorigin + self.ypixelsize * row + self.xrotation * pixel
        return x, y
        
    def getPixel(self, x, y):
        """"""
        # need to figure out how to work the rotation term in, i should be better at math huh?
        # if i really need help i can plug it into a solver (sympy)
        # i also dont see this being the most needed thing though
        xoffset = x - self.xorigin
        yoffset = y - self.yorigin
        # should the offsets be subtracted? for the rotations?
        pixel = xoffset / self.xpixelsize + yoffset / self.yrotation
        row = xoffset / self.xpixelsize + yoffset / self.yrotation
        return pixel, row
    
    def getCorners(self):
        """"""
        mydict = {'nwcorner': (self.xorigin, self.yorigin),
                  'necorner': self.getCoordinate(0, self.width),
                  'secorner': self.getCoordinate(self.height, self.width),
                  'swcorner': self.getCoordinate(self.height, 0)}
        return mydict
        
    @classmethod
    def createWorldFromCorners(cls, corners, raster):
        """"""
        from math import hypot
        fields = ['xpixelsize', 'xrotation', 'yrotation', 'ypixelsize', 'xorigin', 'yorigin']
        average = lambda indict, inkey1, inkey2: (x['utmLat' + inkey1] + x['utmLat' + inkey2]) / 2, (x['utmLon' + inkey1] + x['utmLon' + inkey2]) / 2
        distance = lambda x,y: hypot(x[0] - y[0], x[1] - y[1])
        skew = lambda x, y: (x[1] - y[1]) / (x[0] - y[0])
        leftmean = average(corners, 'NW', 'SW')
        rightmean = average(corners, 'NE', 'SE') 
        topmean = average(corners, 'NW', 'NE')
        bottommean = average(corners, 'SW', 'SE') 
        meterwidth = distance(leftmean, rightmean)
        meterheight = distance(topmean, bottomean)
        pixelcountwidth, pixelcountheight = read_metadata.getSize(raster)
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
