# mike mommsen
# january 2015 
# for HIG
# script to automate the creation of photos for areas with georeferenced photos
from PIL import Image
import logging
import re
from topos_utils import clipByPoly, extentToArcPolygon
import os
from MapDocument import MapDocument, INCHESPERMETER, nad83
from read_metadata import WKID_DICT, PROJ_DICT
import string

# this is the template that allows us to georef images
# we could rework it a bit to make it easier to write to
with open(r'J:\GIS_Data\Working-MikeM\template.jpg.aux.xml') as f:
    text = f.read()
    TEMPLATE = string.Template(text)

################################################
# section of regex patterns to gather data from our image filenames
# the most generic one alpha-roll-frame
COUNTYPATTERN = r'''(?P<county>[a-zA-Z]{2,3})-(?P<roll>[0-9]{1,2})(?P<project>[a-zA-Z]{0,2})-(?P<frame>[0-9]{1,3})'''
# another common one fips-rollyear-frame
COUNTYPATTERN_YEAR_IN_NAME = r'''(?P<county>[0-9]{5})-(?P<roll>[0-9])(?P<year>[0-9]{2})-(?P<frame>[0-9]{3})'''
# for ones like ITA47-01-001
COUNTYPATTERN_MN = r'''(?P<county>[a-zA-Z]{3})(?P<year>[0-9]{2})-(?P<roll>[0-9]{2})-(?P<frame>[0-9]{3})'''
# generic pattern for the indices in county folders
COUNTYINDICES = r'''(?P<county>[a-zA-Z]*)(?P<year>[0-9]{2})-(?P<sheet>[0-9]{2})(?P<agency>[a-zA-Z]*)'''
# hig naming for nhaps
NHAPPATTERN = r'''(?P<project>HAP8[0-5]|02|OK)-(?P<roll>[0-9]{3})-(?P<frame>[0-9]{3})'''
# pattern for doqqs
# we are going to have to write a parser for these
# and i did!!! ohhh boooy!!!!
DOQQPATTERN = r'''(?P<lat>[0-9]{2})(?P<lon>[0-9]{3})(?P<quad>[a-hA-H][1-8])(?P<qq>[nNsS][wWeE])(?P<year>[0-9]{2})'''
# pattern for a lot of the usgs photos  in the city folders
USGSPATTERN = r'''GS-(?P<project>[a-zA-Z]{1-4})-(?P<roll>[0-9]{1,3})-(?P<frame>[0-9]{1,3})'''
# mn dnr uses this so we have it when it is not changed
COUNTYPATTERN_dnr = r'''(?P<county>[a-zA-Z]{2,3})(?P<roll>[0-9]{2})(?P<project>[a-zA-Z]{0,2})(?P<frame>[0-9]{3})'''
#pattern for county mosaics. not really sure what the leading part is though
COUNTYMOSAICPATTERN = r'''ortho_[1-9ns_-]{8}_(?P<state>[a-z]{2})(?P<county>[0-9]{3})_(?P<year>[0-9]{4})_[1-9]'''

# these three functions are slightly modified from the functions that are used in read_metadata to accomadate the workflow here
def cornersToTemplateFormat(corners):
    """takes an arcpy poly with 4 corners and returns a nice field dict to populate the table
    or to make the output aux file, or maybe link table"""
    utmcoords = {}
    for corner, (lat, lon) in corners.iteritems():
        utmcoords[corner.upper() + 'latUTM'] = lat
        utmcoords[corner.upper() + 'lonUTM'] = lon
    return utmcoords

def createAuxFile(coordinates, utmname, inraster, template):
    """takes corner coordinates and a raster and returns the world file."""
    wkid = WKID_DICT[utmname]
    coordinates['wkid'] = wkid
    utmPrjText = PROJ_DICT[utmname]
    coordinates['prj'] = utmPrjText
    output = template.substitute(coordinates)
    outfile = inraster + '.aux.xml'
    with open(outfile, 'w') as f:
        f.write(output)

def doqqDataToCentroid(lat, lon, quad, qq, pixelsize=1):
    """takes the data that is in a doqq filename and returns the centroid of the qq it should cover"""
    # convert the lat lon to float and add 1/32nd of a degree to them
    lat, lon = (1 / 32.) + float(lat), (1 / 32.) + float(lon)
    # basic string and list of numbers used for converting from charecters to index
    letters = 'abcdefgh'
    numbers = [str(x) for x in xrange(1,9)]
    # add the index divided by 8 to the lat and lon
    lat += letters.index(quad[0].lower()) / 8.
    lon +=  numbers.index(quad[1]) / 8.
    # when its south we dont need to shift, but when its north we need to move up
    if qq[0].lower() == 'n':
        lat += 1 / 16.
    # same for west
    if qq[1].lower() == 'w':
        lon += 1 / 16.
    return lat, -lon

def georefDoqq(img, outshp=None, pixelsize=1):
    """"""
    fullpath = img.fullpath
    img.parseBaseName(pattern=DOQQPATTERN)
    centroid = doqqDataToCentroid(lat=img.lat, lon=img.lon, quad=img.quad, qq=img.qq)
    width, height = img.getSize()
    scale = INCHESPERMETER * pixelsize
    md = MapDocument(width=width, height=height, scale=scale, centroid=centroid, inspatialRef=nad83)
    utmname = md.utmname
    corners = md.corners
    coordinates = cornersToTemplateFormat(corners)
    coordinates['width'], coordinates['height'] = width, height
    createAuxFile(coordinates, utmname, fullpath, template=TEMPLATE)
    if outshp:
        md.createArcPolygon(outshp, filename=fullpath)
    return corners

def georefDoqqFolder(infolder, outshp=None, pixelsize=1):
    """takes a folder and feeds the ones that are not georeferenced to georefDoqq"""
    imgs = [Photo(os.path.join(infolder, x))  for x in os.listdir(infolder) if x[-4:].lower() in ('.tif', '.jpg')]
    for img in imgs:
        # if its not georeferenced then we will georeference it
        if not [x for x in img.getSupportFiles() if x[-8:] == '.aux.xml']:
            georefDoqq(img, outshp=outshp, pixelsize=1)
        # if it is we can still write out its shapefile
        else:
            extent = img.getExtent()
            poly = extentToArcPolygon(extent)

def imageExtensionToWorldExtension(imageExtension):
    """"""
    # the logic to turn an image extension to a world extension is easy, but should be its own function
    # if it leads with a dot we send it back with the dot
    index = 3 if imageExtension[0] == '.' else 2
    return imageExtension[:index] + imageExtension[-1] + 'w'

class Photo(object):
    """"""
    def __init__(self, fullpath, date=None, agency=None, roll=None, frame=None, 
        county=None, project=None, flightline=None, logger=logging.getLogger()):
        """"""
        self.fullpath = fullpath  
        self.date = date
        self.agency = agency
        self.roll = roll
        self.frame = frame
        self.county = county
        self.project = project
        self.flightline = flightline
        self.logger = logger

    def __str__(self):
        """"""
        return self.fullpath

    def getDesc(self):
        """"""
        try:
            self.desc = arcpy.Describe(self.fullpath)
            return self.desc
        except Exception as e:
            self.logger.warning('ArcGIS had an error when trying to describe your image. Error: {e} with Image: {fullpath  }'.format(e, self.fullpath))

    def getSpref(self):
        """"""
        # we are going to need to add a clause here for dealing with how this returns a fake spatial reference not null when an image is not georeferenced
        if not hasattr(self, 'desc'):
            self.getDesc()
        self.spref = desc.spatialReference
        return self.spatialReference

    def getSize(self):
        """"""
        try:
            self.width, self.height = Image.open(self.fullpath).size
            return self.width, self.height
        except Exception as e:
            self.logger.warning('PIL had an error: {e} with {fullpath}'.format(e, self.fullpath))

    def getExtent(self):
        """"""
        if not hasattr(self, 'desc'):
            self.getDesc()
        self.extent = desc.extent
        return self.extent

    def clipByPoly(self, outpath, poly):
        """"""
        clipByPoly(poly, self.fullpath, outpath,logger=self.logger)
        self.clippath = outpath
        return True

    def parseFileName(self):
        """"""
        self.directory, self.filename = os.path.split(self.fullpath)
        self.basename, self.extension = os.path.splitext(self.filename)
        return True

    def parseBaseName(self, pattern=COUNTYPATTERN):
        """"""
        if not hasattr(self, 'basename'):
            self.parseFileName()
        m = re.match(pattern, self.basename)
        if m:
            mdict = m.groupdict()
            for k, v in mdict.iteritems():
                setattr(self, k, v)
            return True
        return False

    def getSupportFiles(self):
        """"""
        if not hasattr(self, 'basename'):
            self.parseFileName()
        self.supportFiles = [os.path.join(self.directory, x) for x in os.listdir(self.directory) if x.split('.')[0] == self.basename and x[-len(self.extension):] != self.extension]
        return self.supportFiles

    def getWorldFile(self):
        """"""
        if not hasattr(self, 'supportFiles'):
            self.getSupportFiles()
        worldExtension = imageExtensionToWorldExtension(self.extension)
        mylist = [x for x in self.supportFiles if os.path.splitext(x).lower() in (worldExtension, worldExtension + 'x')]
        if mylist:
            if len(mylist) == 1:
                self.worldFile = os.path.join(self.directory, mylist[0])
            else:
                xlist = [x for x in mylist if 'x' in mylist]
                if xlist:
                    self.worldFile = os.path.join(self.directory, xlist[0])
                else:
                    self.worldFile = None
        else:
            self.worldFile = None
        return self.worldFile

    def parseWorldFile(self):
        """"""
        if not hasattr(self, 'worldFile'):
            self.getWorldFile()
        if not self.worldFile:
            return
        with open(self.worldFile) as f:
            self.worldText = f.read()
        fields = ['ypixelsize', 'xrotation', 'yrotation', 'xpixelsize', 'yorigin', 'xorigin']
        rows = self.worldText.split('\n')
        rows = [x for x in rows if x]
        for f, r in zip(fields, rows[:6]):
            setattr(self, f, float(r))
        self.geo = True
        return True

    def getCoordinate(self, pixel, row):
        """"""
        if self.geo:
            x = self.xorigin + self.xpixelsize * pixel + self.xrotation * row
            y = self.yorigin + self.ypixelsize * row + self.yrotation * pixel
            return x, y

    def getPixel(self, x, y):
        """"""
        if self.geo:
            denom = self.xpixelsize * self.ypixelsize - self.yrotation * self.xrotation
            pixel = (self.ypixelsize * x - self.xrotation * y + self.xrotation * self.yorigin - self.ypixelsize * self.xorigin) / denom
            row = (-self.yrotation * x + self.xpixelsize * y + self.yrotation * self.xorigin - self.xpixelsize * self.yorigin) / denom
            return pixel, row
    
    def getCorners(self):
        """"""
        if self.geo:
            self.corners = {'NW': self.getCoordinate(-.5,-.5),
                            'NE': self.getCoordinate(-.5,self.width-.5),
                            'SE': self.getCoordinate(self.height-.5, self.width-.5),
                            'SW': self.getCoordinate(self.height-.5, -.5)}
            return self.corners

    def getArcPolygon(self, outspref=None):
        """"""
        if self.geo:
            corners = self.getCorners()
            corners = {k: arcpy.PointGeometry(arcpy.Point(X=v[1], Y=v[0]), self.spref) for k, v in corners.iteritems()}
            if outspref:
                corners = {k: v.projectAs(outspref) for k, v in corners.iteritems()}
            ar = arcpy.Array()
            # add each corner and the first one twice
            ar.add(corners['NW'])
            ar.add(corners['NE'])
            ar.add(corners['SE'])
            ar.add(corners['SW'])
            ar.add(corners['NW'])
            # return it as a polygon
            return arcpy.Polygon(ar, spatialReference)
