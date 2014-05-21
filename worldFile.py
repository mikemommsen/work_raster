import sys
import os

# make sure that we import WORLD_FILES and read_metadata

class WorldFile(Object):
    """"""
    def __init__(self, raster=None):
        """"""
        self.raster = raster
        self.width, self.height = read_metadata.getSize(raster)
        self.directory, self.filename = os.path.split(raster)
        self.basefilename, self.extension = os.path.splitext(self.filename)
        # think about maybe storing full paths (os.path.join(self.directory, x))
        self.supportFiles = [x for x in os.listdir(self.directory) if x.split('.')[0] == self.basefilename]
        if not self.supportFiles:
            print 'we dont have any support files, this is a problem'
        else:
            worldFiles = [x for x in self.supportFiles if x in WORLD_FILES]
            # if there is only one use it
            if len(worldFiles) == 1:
                self.worldFile = worldFiles[0]
            # if there are more than one
            elif len(worldFiles) > 1:
                xfile =  [x for x in in worldFiles if 'x' in x]
                if xfile:
                    self.worldFile = xfile
                else:
                    print 'no way of knowing which file is your world file'
            else:
                print 'could not find a world file'
            
    def __str__(self):
        """"""
        return self.raster
        
    def parseWorldFile(self):
        """"""
        with open(os.path.join(self.directory, self.worldFile)) as f:
            self.worldText = f.read
        rows = self.worldText.split('\n')
        fields = ['xpixelsize', 'xrotation', 'yrotation', 'ypixelsize', 'xorigin', 'yorigin']
        for field, row in zip(fields, rows):
            setattr(self, field, row)
            
    def writeWorldFile(self, outfile):
        """"""
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
        mydict = {'nwcorner': self.xorigin, self.yorigin,
                  'necorner': self.getCoordinate(0, self.width),
                  'secorner': self.getCoordinate(self.height, self.width),
                  'swcorner': self.getCoordinate(self.height, 0)}
        return mydict
        
    @classmethod
    def createWorldFromCorners(cls, corners, raster):
        """"""
        from math import hypot
        fields = ['xpixelsize', 'xrotation', 'yrotation', 'ypixelsize', 'xorigin', 'yorigin']
        average = lambda indict, inkey1, inkey2: (x['utmLat' + inkey1] + x['utmLat' + inkey2]) / 2,
                                           (x['utmLon' + inkey1] + x['utmLon' + inkey2]) / 2
        distance = lambda x,y: hypot(x[0] - y[0], x[1] - y[1])
        skew = lambda x, y: (x[1] - y]1]) / (x[0] - y[0])
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
