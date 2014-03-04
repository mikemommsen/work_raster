import sys
from bs4 import BeautifulSoup
import urllib2
import json
import time
import geojson
import re

G_RING_MATCHER = r'G-Ring_(Latitude|Longitude):\s*([-+]?\d*\.\d+|\d+)'

CORNERS = {
           'NW': ('NW Corner Lat dec', 'NW Corner Long dec'), 
           'NE': ('NE Corner Lat dec', 'NE Corner Long dec'), 
           'SE': ('SE Corner Lat dec', 'SE Corner Long dec'), 
           'SW': ('SW Corner Lat dec', 'SW Corner Long dec')
           }

def readmetadatafdgc(url):
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
    """"""
           
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

def createoutput(indict):
    mylist = []
    for corner, coords in CORNERS.iteritems():
        lat, lon = [float(indict[x]) for x in coords]
        mylist.append((lon,lat))
    multi = geojson.MultiPoint(mylist)
    return multi

def main():
    url = sys.argv[1]
    outpath = sys.argv[2]
    mydict = readmetadata(url)
    output = createoutput(mydict)
    print output

if __name__ == '__main__':
    main()

