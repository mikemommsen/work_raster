import sys
import os

class WorldFile(Object):
    """"""
    def __init__(self, raster=None):
        """"""
        self.raster = raster
        self.width, self.height = read_metadata.getSize(raster)
        self.directory, self.filename = os.path.split(raster)
        self.basefilename, self.extension = os.path.splitext(self.filename)
        

def main():
    pass
    
if __name__ == '__main__':
    main()
