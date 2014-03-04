# mike mommsen
# march 2014

# import parts of the standard library that are going to be used
# this is my first time importing non standard modules in functions themselves, but it seems like a good idea

import sys
import urllib2
import json
import time
import re

# re to find the rinds g ring coords in fgdc metadata
G_RING_MATCHER = r'G-Ring_(Latitude|Longitude):\s*([-+]?\d*\.\d+|\d+)'

#the keys for the corners in the table metadata
CORNERS = {'NW': ('NW Corner Lat dec', 'NW Corner Long dec'), 
           'NE': ('NE Corner Lat dec', 'NE Corner Long dec'), 
           'SE': ('SE Corner Lat dec', 'SE Corner Long dec'), 
           'SW': ('SW Corner Lat dec', 'SW Corner Long dec')}

def readcoordinatesfdgc(url):
    """reads a metadata fdgc table for a earthexplorer raster and returns the four corners.
    the format for the points right now is a list with four tuples of latitude and longitude in decimal degrees.
    a more logical way would be a point from a program that can be written in wkt, wkb, geojson etc
    maybe we can find something for that"""
    mydict = {}
    f = urllib2.urlopen(url)
    content = f.read()
    mylist = re.findall(G_RING_MATCHER, content)
    Latitudes = [y for x, y in mylist if y = 'Latitude']
    Longitudes = [y for x, y in mylist if y = 'Longitude']
    return zip(Latitudes, Longitudes)
    
def readmetadatatable(url):
    """takes a url to an earthexplorer table metadata file and returns the metadata in a  dictionary"""
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
        geom = geojson.MultiPoint(incoordinates)
        # we should check to see if indent causes any problems for programs parsers
        # but i dont thing that it should
        goejson.dump(geom, indent=4)
        
def writeshapefile(incoordinates, outfile):
    """"""
    try:
        import arcpy
    except ImportError as e:
        print e
        sys.exit(1)
        #more details about not having arcpy, or an attempt to use shapefile, not a bad idea actually
    if not arcpy.exists(outfile):
        arcpy.CreateFeatureclass_management(*os.path.split(outfile), "Polygon", "", "", "", 
        """GEOGCS["WGS 84", 
            DATUM["WGS_1984", 
            SPHEROID["WGS 84", 6378137.0, 298.257223563, AUTHORITY["EPSG","7030"]], 
            TOWGS84[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 
            AUTHORITY["EPSG","6326"]], 
            PRIMEM["Greenwich", 0.0, AUTHORITY["EPSG","8901"]], 
            UNIT["degree", 0.017453292519943295], 
            AXIS["Longitude", EAST], 
            AXIS["Latitude", NORTH], 
            AUTHORITY["EPSG","4326"]])"""
    cur = arcpy.InsertCursor(outfile)
        
    
    

def main():
    url = sys.argv[1]
    outpath = sys.argv[2]
    output = readcoordinatesfdgc(url)
    print output

if __name__ == '__main__':
    main()

