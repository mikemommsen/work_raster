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
        

def main():
    pass
    
if __name__ == '__main__':
    main()
