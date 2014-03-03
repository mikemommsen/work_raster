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
    mydict = {}
    f = urllib2.urlopen(url)
    content = f.read()
    mylist = re.findall(G_RING_MATCHER, content)
    print mylist
    
def readmetadatatable(url):
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

