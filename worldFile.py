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
        worldFiles = [x for x in self.supportFiles if x in WORLD_FILES]
        if len(worldFiles) == 1:
            self.worldFile = worldFiles[0]
        else:
            self.worldFile =  [x for x in in worldFiles if 'x' in x][0]
            
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
        width = distance(leftmean, rightmean)
        height = distance(topmean, bottomean)
        pixelwidth, pixelheight = read_metadata.getSize(raster)
        fields = [pixelwidth]
        fields += [skew(bottommean, topmean)]
        fields += [skew(leftmean, rightmean)]
        fields += [pixelheight]
        fields += []
        fields += []
        rows = []
        nwcorner
        hypot for pixelsize
        with open(raster.split('.')[0] + 'jgw') as f:
            f.write(self.worldText)
        return cls(raster)
        
def main():
    """"""
    pass
    
if __name__ == '__main__':
    main()
