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
FIELDS = ['Entity ID', 'Agency', 'Recording Technique', 
          'Project', 'Roll', 'Frame', 'Acquisition Date', 
          'Scale',  'Image Type', 'Quality', 'Cloud Cover', 
          'Photo ID', 'Flying Height in Feet', 'Film Length and Width',
          'Focal Length', 'Stereo Overlap']
           
def readmetadatafgdc(url):
    """"""
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
   
def readmetadatacsv(infile):
    """i dont have bs4 at work right now so i am downloading metadata and parsing it as a csv.
    this serves no other purpose outside of testing"""
    with open(infile) as f:
        reader = csv.reader(f)
        mydict = {k: v for k, v in reader}
    return mydict
    
def readcoordinatescsv(indict):
    mylist = []
    for lat, lon in CORNERS.values():
        mylist.append(float(indict[lat]), float(indict[lon]))
    return mylist
    
def readmetadatatable(url):
    """takes a url to an earthexplorer table metadata file and returns the metadata in a dictionary"""
    try:
        from bs4 import BeautifulSoup
    except ImportError as e:
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

def readcoordinatestable(url):
    """takes a url and returns the coordinates of the corners"""
    indict = readmetadatatable(url)
    mylist = []
    for corner, coords in CORNERS.iteritems():
        lat, lon = [float(indict[x]) for x in coords]
        mylist.append((lat,lon))
    return mylist
    
def writegeojson(incoordinates, outfile):
    """"""
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
    for field in FIELDS:
        arcpy.AddField_management(feature, field, "TEXT")
        
def writeshapefile(incoordinates, outfile, oid, field_data):
    """"""
    try:
        import arcpy
    except ImportError as e:
        print e
        sys.exit(1)
        #more details about not having arcpy, or an attempt to use shapefile, not a bad idea actually
    if not arcpy.Exists(outfile):
        basepath, filename = os.path.split(outfile)
        createnewshapefile(basepath, filename)
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
    for key, value in field_data:
        newrow.setValue(key, value)
    cur.insertRow(newrow)
    del newrow, cur
    return True
    
def filterdict(indict, inlist):
    """takes a dict and returns the a new dict with the keys that are in the list"""
    return {k: v for k, v in indict if k in inlist}
    
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
    
def main():
    url = sys.argv[1]
    outpath = sys.argv[2]
    #coordinates = readcoordinatesfdgc(url)
    alldata = readmetadatacsv(infile)
    # this could be dumped into the geojson properties or attributes or whatever they call it in geojson
    field_data = filterdict(alldata, FIELDS)
    coordinates = readcoordinatescsv(alldata)
    outbasepath, outfile = os.path.split(outpath)
    outfilename, outfileextension = os.path.splitext(outfile)
    if outfileextension == '.shp':
        # not sure if we even need to make a new oid, or if we can go about this in some other way
        oid = findNextOid(outpath)
        writeshapefile(coordinates, outpath, oid, field_data)
    elif outfileextension in ['.json', '.geojson']:
        writegeojson(coordinates, outpath)
    print True

if __name__ == '__main__':
    main()
