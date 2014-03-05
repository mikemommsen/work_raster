# mike mommsen
# march 2014


# import parts of the standard library that are going to be used
# this is my first time importing non standard modules in functions themselves, but it seems like a good idea
import sys
import urllib2
import json
import time
import re
import os
import csv
from collections import OrderedDict

# re to find the rinds g ring coords in fgdc metadata
G_RING_MATCHER = r'G-Ring_(Latitude|Longitude):\s*([-+]?\d*\.\d+|\d+)'

#the keys for the corners in the table metadata
CORNERS = OrderedDict({'NW': ('NW Corner Lat dec', 'NW Corner Long dec'),
           'NE': ('NE Corner Lat dec', 'NE Corner Long dec'),
           'SE': ('SE Corner Lat dec', 'SE Corner Long dec'),
           'SW': ('SW Corner Lat dec', 'SW Corner Long dec')})
           
# list of the fields that i think would be nice in the output
# this is a dictionary with the key being the name that is in the metadata and the value the name that is shapefile safe
FIELDS = OrderedDict({'Entity  ID':'title', 
          'Agency':'Agency', 
          'Recording Technique':'rec_tech', 
          'Project':'Project', 
          'Roll': 'Roll', 
          'Frame': 'Frame', 
          'Acquisition Date':'Acqdate', 
          'Scale':'scale',  
          'Image Type':'imgtype', 
          'Quality':'Quality', 
          'Cloud Cover':'cloudcover', 
          'Photo ID':'photoid', 
          'Flying Height in Feet':'heightFt', 
          'Film Length and Width':'filmsize',
          'Focal Length':'focallen', 
          'Stereo Overlap':'overlap'})
           
def readmetadatafgdc(url):
    """reads the fgdc metadata - not sure if this is going to be used very much
    also consider the fact that other people probably already have parsers that actually work for fgdc
    arc even parses it, so we should not be bootlegging it"""
    mydict = {}
    f = urllib2.urlopen(url)
    content = f.read()
    for row in content.split('\n'):
        if row.count(':') == 1:
            key, val = row.strip(' ').split(':')
            if key and val:
                mydict[key] = val
    return mydict

def readcoordinatesfdgc(url):
    """reads a metadata fdgc table for a earthexplorer raster and returns the four corners.
the format for the points right now is a list with four tuples of latitude and longitude in decimal degrees.
a more logical way would be a point from a program that can be written in wkt, wkb, geojson etc
maybe we can find something for that"""
    mydict = {}
    f = urllib2.urlopen(url)
    content = f.read()
    mylist = re.findall(G_RING_MATCHER, content)
    print mylist
    Latitudes = [float(y) for x, y in mylist if x == 'Latitude']
    Longitudes = [float(y) for x, y in mylist if x == 'Longitude']
    return zip(Latitudes, Longitudes)
    
def readmetadatatable(url):
    """takes a url to an earthexplorer table metadata file and returns the metadata in a dictionary"""
    try:
        from bs4 import BeautifulSoup
    except ImportError as e:
        # maybe put in some info here for people so they know they need bs4
        print e
        sys.exit(1)
    mydict = {}
    f = urllib2.urlopen(url)
    content = f.read()
    soup = BeautifulSoup(content)
    for row in soup('table')[0].findAll('tr'):
        tds = row('td')
        if tds and len(tds) == 2:
            key, value = [td.text for td in tds]
            mydict[key] = value
    return mydict

def readcoordinatestable(indict):
    """takes a url and returns the coordinates of the corners"""
    mylist = []
    for corner, coords in CORNERS.iteritems():
        lat, lon = [float(indict[x]) for x in coords]
        mylist.append((lat,lon))
    return mylist
    
def writegeojson(incoordinates, outfile):
    """takse coordinates and writes them to an outfile"""
    # there is still a decent amount of work to do on this
    # do we want it to be points, polys, or something else
    # also if the file exists we probably want to append and not write over the old file
    try:
        import geojson
    except ImportError as e:
        print e
        sys.exit(1)
        #maybe more things here to let people know the problem of not having geojson for python
    with open(outfile, 'w') as f:
        geom = geojson.MultiPoint([(y, x) for x, y in incoordinates])
        # we should check to see if indent causes any problems for programs parsers
        # but i dont thing that it should
        geojson.dump(geom, f, indent=4)
        
def createnewshapefile(basepath, filename):
    """takes a path and name and creates a new featureclass.
    although not explicityle required to be a shapefile that is the general goal here"""
    feature = arcpy.CreateFeatureclass_management(basepath, filename, "POLYGON", "", "", "",
        """GEOGCS["WGS 84",
        DATUM["WGS_1984",
        SPHEROID["WGS 84", 6378137.0, 298.257223563, AUTHORITY["EPSG","7030"]],
        TOWGS84[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        AUTHORITY["EPSG","6326"]],
        PRIMEM["Greenwich", 0.0, AUTHORITY["EPSG","8901"]],
        UNIT["degree", 0.017453292519943295],
        AXIS["Longitude", EAST],
        AXIS["Latitude", NORTH],
        AUTHORITY["EPSG","4326"]])""")
    # add the fields
    # there is probably a better way to specify fields for a new shapefile than adding them one at a time huh?
    for field in FIELDS.values():
        arcpy.AddField_management(feature, field, "TEXT")
        
def writeshapefile(incoordinates, outfile, field_data):
    """takes coordinates and field_data and writes to the outfile"""
    try:
        import arcpy
    except ImportError as e:
        # could include some more details about person not having arcpy on their computer
        print e
        sys.exit(1)
    # if the file does not exist then we have to make it 
    if not arcpy.Exists(outfile):
        basepath, filename = os.path.split(outfile)
        createnewshapefile(basepath, filename)
        oid = 1
    # if the file does exist find the next availible oid
    else:
        oid = findNextOid(outfile)
    # start up a cursor - this makes me think that we should make this something that can be bulk loaded with a list of coordinates
    # all of this stuff for adding a feature to a featureclass is all from arcpy documentation on cursors so more can be found there
    cur = arcpy.InsertCursor(outfile)
    newrow = cur.newRow()
    newrow.id = oid
    arrayObj = arcpy.Array()
    pnt = arcpy.Point()
    for lat, lon in incoordinates:
        pnt.X, pnt.Y = lon, lat 
        arrayObj.add(pnt)
    poly = arcpy.Polygon(arrayObj)
    newrow.shape = arrayObj
    for key, value in field_data.iteritems():
        newrow.setValue(key, value)
    cur.insertRow(newrow)
    # should we have a try here, because if it fails we will probably destroy the feature class
    del newrow, cur
    # probably dont need to return anything here huh?
    return True
    
def filterdata(datadict, fielddict):
    """takes a datadict and returns the values that have keys in the fielddict along with the value from the fielddict"""
    mydict = {v: datadict.get(k, 'NULL') for k, v in fielddict.iteritems()}
    return mydict
    
def findNextOid(infeature):
    """takes an infeature, finds the maximum oid, and returns a number one higher."""
    cur = arcpy.SearchCursor(infeature)
    mylist = [0]
    for r in cur:
        mylist.append(r.id)
    if 'r' in vars().keys():
        del r
    del cur
    return max(mylist) + 1
    
def getsize(inraster):
    """this gets the size of the raster using PIL"""
    # is PIL part of the standard library?
    # if so we can move this import up to the top
    from PIL import Image
    i = image.open(inraster)
    width, height = i.size
    return width, height
    
def getutmzone(longitude):
    """takes a wgs84 longitude and returns the utm zone"""
    utms = range(-180, 180, 6)

    
def createworldfile(coordinates, pixels, rows):
    
    
def main():
    """"""
    url = sys.argv[1]
    outpath = sys.argv[2]
    alldata = readmetadatatable(url)
    # this could be dumped into the geojson properties or attributes or whatever they call it in geojson
    field_data = filterdata(alldata, FIELDS)
    coordinates = readcoordinatescsv(alldata)
    outbasepath, outfile = os.path.split(outpath)
    outfilename, outfileextension = os.path.splitext(outfile)
    if outfileextension == '.shp':
        writeshapefile(coordinates, outpath, field_data)
    elif outfileextension in ['.json', '.geojson']:
        writegeojson(coordinates, outpath)
    print True

if __name__ == '__main__':
    main()
