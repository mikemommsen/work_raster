# mike mommsen
# march 2014

import sys
import urllib2
import json
import time
import re
import os
from collections import OrderedDict
import string
import arcpy

# this is used by multiple functions so we are saving it as global
wgs84 = arcpy.SpatialReference('WGS 1984')
# keys are utm names, values are the wkid needed in the aux file
WKID_DICT = {
    "NAD 1983 UTM Zone 10N": "26910", 
    "NAD 1983 UTM Zone 11N": "26911", 
    "NAD 1983 UTM Zone 12N": "26912", 
    "NAD 1983 UTM Zone 13N": "26913", 
    "NAD 1983 UTM Zone 14N": "26914", 
    "NAD 1983 UTM Zone 15N": "26915", 
    "NAD 1983 UTM Zone 16N": "26916", 
    "NAD 1983 UTM Zone 17N": "26917", 
    "NAD 1983 UTM Zone 18N": "26918", 
    "NAD 1983 UTM Zone 19N": "26919"
    }
    
PROJ_DICT = {
    "NAD 1983 UTM Zone 10N": "PROJCS[&quot;NAD_1983_UTM_Zone_10N&quot;,GEOGCS[&quot;GCS_North_American_1983&quot;,DATUM[&quot;D_North_American_1983&quot;,SPHEROID[&quot;GRS_1980&quot;,6378137.0,298.257222101]],PRIMEM[&quot;Greenwich&quot;,0.0],UNIT[&quot;Degree&quot;,0.0174532925199433]],PROJECTION[&quot;Transverse_Mercator&quot;],PARAMETER[&quot;False_Easting&quot;,500000.0],PARAMETER[&quot;False_Northing&quot;,0.0],PARAMETER[&quot;Central_Meridian&quot;,-123.0],PARAMETER[&quot;Scale_Factor&quot;,0.9996],PARAMETER[&quot;Latitude_Of_Origin&quot;,0.0],UNIT[&quot;Meter&quot;,1.0],AUTHORITY[&quot;EPSG&quot;,26910]]\n", 
    "NAD 1983 UTM Zone 11N": "PROJCS[&quot;NAD_1983_UTM_Zone_11N&quot;,GEOGCS[&quot;GCS_North_American_1983&quot;,DATUM[&quot;D_North_American_1983&quot;,SPHEROID[&quot;GRS_1980&quot;,6378137.0,298.257222101]],PRIMEM[&quot;Greenwich&quot;,0.0],UNIT[&quot;Degree&quot;,0.0174532925199433]],PROJECTION[&quot;Transverse_Mercator&quot;],PARAMETER[&quot;False_Easting&quot;,500000.0],PARAMETER[&quot;False_Northing&quot;,0.0],PARAMETER[&quot;Central_Meridian&quot;,-117.0],PARAMETER[&quot;Scale_Factor&quot;,0.9996],PARAMETER[&quot;Latitude_Of_Origin&quot;,0.0],UNIT[&quot;Meter&quot;,1.0],AUTHORITY[&quot;EPSG&quot;,26911]]\n", 
    "NAD 1983 UTM Zone 12N": "PROJCS[&quot;NAD_1983_UTM_Zone_12N&quot;,GEOGCS[&quot;GCS_North_American_1983&quot;,DATUM[&quot;D_North_American_1983&quot;,SPHEROID[&quot;GRS_1980&quot;,6378137.0,298.257222101]],PRIMEM[&quot;Greenwich&quot;,0.0],UNIT[&quot;Degree&quot;,0.0174532925199433]],PROJECTION[&quot;Transverse_Mercator&quot;],PARAMETER[&quot;False_Easting&quot;,500000.0],PARAMETER[&quot;False_Northing&quot;,0.0],PARAMETER[&quot;Central_Meridian&quot;,-111.0],PARAMETER[&quot;Scale_Factor&quot;,0.9996],PARAMETER[&quot;Latitude_Of_Origin&quot;,0.0],UNIT[&quot;Meter&quot;,1.0],AUTHORITY[&quot;EPSG&quot;,26912]]\n", 
    "NAD 1983 UTM Zone 13N": "PROJCS[&quot;NAD_1983_UTM_Zone_13N&quot;,GEOGCS[&quot;GCS_North_American_1983&quot;,DATUM[&quot;D_North_American_1983&quot;,SPHEROID[&quot;GRS_1980&quot;,6378137.0,298.257222101]],PRIMEM[&quot;Greenwich&quot;,0.0],UNIT[&quot;Degree&quot;,0.0174532925199433]],PROJECTION[&quot;Transverse_Mercator&quot;],PARAMETER[&quot;False_Easting&quot;,500000.0],PARAMETER[&quot;False_Northing&quot;,0.0],PARAMETER[&quot;Central_Meridian&quot;,-105.0],PARAMETER[&quot;Scale_Factor&quot;,0.9996],PARAMETER[&quot;Latitude_Of_Origin&quot;,0.0],UNIT[&quot;Meter&quot;,1.0],AUTHORITY[&quot;EPSG&quot;,26913]]\n", 
    "NAD 1983 UTM Zone 14N": "PROJCS[&quot;NAD_1983_UTM_Zone_14N&quot;,GEOGCS[&quot;GCS_North_American_1983&quot;,DATUM[&quot;D_North_American_1983&quot;,SPHEROID[&quot;GRS_1980&quot;,6378137.0,298.257222101]],PRIMEM[&quot;Greenwich&quot;,0.0],UNIT[&quot;Degree&quot;,0.0174532925199433]],PROJECTION[&quot;Transverse_Mercator&quot;],PARAMETER[&quot;False_Easting&quot;,500000.0],PARAMETER[&quot;False_Northing&quot;,0.0],PARAMETER[&quot;Central_Meridian&quot;,-99.0],PARAMETER[&quot;Scale_Factor&quot;,0.9996],PARAMETER[&quot;Latitude_Of_Origin&quot;,0.0],UNIT[&quot;Meter&quot;,1.0],AUTHORITY[&quot;EPSG&quot;,26914]]\n", 
    "NAD 1983 UTM Zone 15N": "PROJCS[&quot;NAD_1983_UTM_Zone_15N&quot;,GEOGCS[&quot;GCS_North_American_1983&quot;,DATUM[&quot;D_North_American_1983&quot;,SPHEROID[&quot;GRS_1980&quot;,6378137.0,298.257222101]],PRIMEM[&quot;Greenwich&quot;,0.0],UNIT[&quot;Degree&quot;,0.0174532925199433]],PROJECTION[&quot;Transverse_Mercator&quot;],PARAMETER[&quot;False_Easting&quot;,500000.0],PARAMETER[&quot;False_Northing&quot;,0.0],PARAMETER[&quot;Central_Meridian&quot;,-93.0],PARAMETER[&quot;Scale_Factor&quot;,0.9996],PARAMETER[&quot;Latitude_Of_Origin&quot;,0.0],UNIT[&quot;Meter&quot;,1.0],AUTHORITY[&quot;EPSG&quot;,26915]]\n", 
    "NAD 1983 UTM Zone 16N": "PROJCS[&quot;NAD_1983_UTM_Zone_16N&quot;,GEOGCS[&quot;GCS_North_American_1983&quot;,DATUM[&quot;D_North_American_1983&quot;,SPHEROID[&quot;GRS_1980&quot;,6378137.0,298.257222101]],PRIMEM[&quot;Greenwich&quot;,0.0],UNIT[&quot;Degree&quot;,0.0174532925199433]],PROJECTION[&quot;Transverse_Mercator&quot;],PARAMETER[&quot;False_Easting&quot;,500000.0],PARAMETER[&quot;False_Northing&quot;,0.0],PARAMETER[&quot;Central_Meridian&quot;,-87.0],PARAMETER[&quot;Scale_Factor&quot;,0.9996],PARAMETER[&quot;Latitude_Of_Origin&quot;,0.0],UNIT[&quot;Meter&quot;,1.0],AUTHORITY[&quot;EPSG&quot;,26916]]\n", 
    "NAD 1983 UTM Zone 17N": "PROJCS[&quot;NAD_1983_UTM_Zone_17N&quot;,GEOGCS[&quot;GCS_North_American_1983&quot;,DATUM[&quot;D_North_American_1983&quot;,SPHEROID[&quot;GRS_1980&quot;,6378137.0,298.257222101]],PRIMEM[&quot;Greenwich&quot;,0.0],UNIT[&quot;Degree&quot;,0.0174532925199433]],PROJECTION[&quot;Transverse_Mercator&quot;],PARAMETER[&quot;False_Easting&quot;,500000.0],PARAMETER[&quot;False_Northing&quot;,0.0],PARAMETER[&quot;Central_Meridian&quot;,-81.0],PARAMETER[&quot;Scale_Factor&quot;,0.9996],PARAMETER[&quot;Latitude_Of_Origin&quot;,0.0],UNIT[&quot;Meter&quot;,1.0],AUTHORITY[&quot;EPSG&quot;,26917]]\n", 
    "NAD 1983 UTM Zone 18N": "PROJCS[&quot;NAD_1983_UTM_Zone_18N&quot;,GEOGCS[&quot;GCS_North_American_1983&quot;,DATUM[&quot;D_North_American_1983&quot;,SPHEROID[&quot;GRS_1980&quot;,6378137.0,298.257222101]],PRIMEM[&quot;Greenwich&quot;,0.0],UNIT[&quot;Degree&quot;,0.0174532925199433]],PROJECTION[&quot;Transverse_Mercator&quot;],PARAMETER[&quot;False_Easting&quot;,500000.0],PARAMETER[&quot;False_Northing&quot;,0.0],PARAMETER[&quot;Central_Meridian&quot;,-75.0],PARAMETER[&quot;Scale_Factor&quot;,0.9996],PARAMETER[&quot;Latitude_Of_Origin&quot;,0.0],UNIT[&quot;Meter&quot;,1.0],AUTHORITY[&quot;EPSG&quot;,26918]]\n", 
    "NAD 1983 UTM Zone 19N": "PROJCS[&quot;NAD_1983_UTM_Zone_19N&quot;,GEOGCS[&quot;GCS_North_American_1983&quot;,DATUM[&quot;D_North_American_1983&quot;,SPHEROID[&quot;GRS_1980&quot;,6378137.0,298.257222101]],PRIMEM[&quot;Greenwich&quot;,0.0],UNIT[&quot;Degree&quot;,0.0174532925199433]],PROJECTION[&quot;Transverse_Mercator&quot;],PARAMETER[&quot;False_Easting&quot;,500000.0],PARAMETER[&quot;False_Northing&quot;,0.0],PARAMETER[&quot;Central_Meridian&quot;,-69.0],PARAMETER[&quot;Scale_Factor&quot;,0.9996],PARAMETER[&quot;Latitude_Of_Origin&quot;,0.0],UNIT[&quot;Meter&quot;,1.0],AUTHORITY[&quot;EPSG&quot;,26919]]\n"
    }

#the keys for the corners in the table metadata
CORNERS = OrderedDict({
    'NW': ('NW Corner Lat dec', 'NW Corner Long dec'),
    'NE': ('NE Corner Lat dec', 'NE Corner Long dec'),
    'SE': ('SE Corner Lat dec', 'SE Corner Long dec'),
    'SW': ('SW Corner Lat dec', 'SW Corner Long dec')
    })
           
# list of the fields that i think would be nice in the output
# this is a dictionary with the key being the name that is in the metadata and the value the name that is shapefile safe
FIELDS = OrderedDict({
    'Entity  ID':'title', 
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
    'Stereo Overlap':'overlap'
    })
           
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
    gRingMatcher = r'G-Ring_(Latitude|Longitude):\s*([-+]?\d*\.\d+|\d+)'
    mydict = {}
    f = urllib2.urlopen(url)
    content = f.read()
    mylist = re.findall(gRingMatcher, content)
    print mylist
    Latitudes = [float(y) for x, y in mylist if x == 'Latitude']
    Longitudes = [float(y) for x, y in mylist if x == 'Longitude']
    return zip(Latitudes, Longitudes)
    
def readmetadatatable(url):
    """takes a url to an earthexplorer table metadata file and returns the metadata in a dictionary"""
    try:
        from bs4 import BeautifulSoup
    except ImportError as e:
        arcpy.AddMessage('you need bs4 installed to read the internet\n. not really but mike isnt smart enough for that')
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
    for corner in ['NW', 'NE', 'SE', 'SW']:
        coords = CORNERS[corner]
        lat, lon = [float(indict[x]) for x in coords]
        mylist.append((lat,lon))
    return mylist
        
def readFeatureClass(featureClassPath, utmzone, geometryFieldName, photoNameFieldName):
    """"""
    cur = arcpy.SearchCursor(featureClassPath, utmzome)
    try:
        outdict = {}
        for row in cur:
            poly = row.getValue(geometryFieldName)
            photoName = row.getValue(photoNameFieldName)
            unSortedCoordinates = [(pt.X, pt.Y) for pt in poly[0]]
            eastwest = sorted(unSortedCoordinates, key=lambda x: x[1])
            easterns, westerns = eastwest[:2], eastwest[2:]
            sw, nw = sorted(westerns, key=lambda x: x[0])
            se, ne = sorted(easterns, key=lambda x: x[0])
            outdict[photoName] = {
                'SWlatUTM': sw[1], 'SWlonUTM': sw[0], 'NWlatUTM': nw[1], 'NWlonUTM': nw[0], 
                'NElatUTM': ne[1], 'NElonUTM': ne[0], 'SElatUTM': se[1], 'SElonUTM': se[0]}
        return outdict
    except Exception as e:
        print e
        sys.exit(1)
    finally:
        if 'r' in locals():
            del r
        if 'cur' in locals():
            del cur

def createnewshapefile(basepath, filename):
    """takes a path and name and creates a new featureclass.
    although not explicityle required to be a shapefile that is the general goal here"""
    feature = arcpy.CreateFeatureclass_management(basepath, filename, "POLYGON", "", "", "", wgs84)
    # add the fields
    # there is probably a better way to specify fields for a new shapefile than adding them one at a time huh?
    for field in FIELDS.values():
        arcpy.AddField_management(feature, field, "TEXT")
    # seems like there is some overhead considering i make a dict with all these names in it in createUtmCoords
    for corner in ['NW', 'NE', 'SE', 'SW']:
        lat = corner + 'latUTM'
        lon = corner + 'lonUTM'
        arcpy.AddField_management(feature, lat, "DOUBLE")
        arcpy.AddField_management(feature, lon, "DOUBLE")
    arcpy.AddField_management(feature,'utmzone','TEXT')

def createPolygon(incoordinates):
    """takes lat lon incoordinates and returns an arcpy polygon"""
    arrayObj = arcpy.Array()
    pnt = arcpy.Point()
    for lat, lon in incoordinates:
        pnt.X, pnt.Y = lon, lat
        arrayObj.add(pnt)
    poly = arcpy.Polygon(arrayObj, wgs84)
    return poly
    
def createUtmCoords(poly, utmname):
    """takes an arcpy poly with 4 corners and returns a nice field dict to populate the table
    or to make the output aux file, or maybe link table"""
    utmsref = arcpy.SpatialReference(utmname)
    utmpoly = poly.projectAs(utmsref)
    utmcoords = {}
    for part in utmpoly:
        for corner, point in zip(['NW', 'NE', 'SE', 'SW'], part):
            lon, lat = point.X, point.Y
            latfield, lonfield = corner + 'latUTM', corner + 'lonUTM'
            utmcoords[latfield] = lat
            utmcoords[lonfield] = lon
    return utmcoords
    
def writeshapefile(incoordinates, outfile, field_data):
    """takes coordinates and field_data and writes to the outfile"""
    if not arcpy.Exists(outfile):
        basepath, filename = os.path.split(outfile)
        createnewshapefile(basepath, filename)
        oid = 1
    # if the file does exist find the next availible oid
    else:
        oid = findNextOid(outfile)
    # start up a cursor - this makes me think that we should make this something that can be bulk loaded with a list of coordinates
    # all of this stuff for adding a feature to a featureclass is all from arcpy documentation on cursors so more can be found there
    utmname = getutmzone(sum(lon for lat, lon in incoordinates)/len(incoordinates))
    poly = createPolygon(incoordinates)
    cur = arcpy.InsertCursor(outfile)
    newrow = cur.newRow()
    newrow.id = oid
    newrow.setValue('utmzone', utmname)
    # create a wgs84 spatialReference
    newrow.shape = poly
    for key, value in field_data.iteritems():
        newrow.setValue(key, value)
    utmcoords = createUtmCoords(poly, utmname)
    for field, val in utmcoords.iteritems():
        newrow.setValue(field, val)
    cur.insertRow(newrow)
    # should we have a try here, because if it fails we will probably destroy the feature class
    del newrow, cur
    return utmcoords, utmname
    
def filterdata(datadict, fielddict):
    """takes a datadict and returns the values that have keys in the fielddict along with the value from the fielddict"""
    # this could be a good place to get data from napps that is not coming through
    # i dont know if the metadata is different for napps, or if there is just less of it
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
    
def getsizePIL(inraster):
    """this gets the size of the raster using PIL"""
    from PIL import Image
    i = Image.open(inraster)
    width, height = i.size
    return width, height
    
def getsize(inraster):
    """gets the size of the raster using arcpy"""
    try:
        desc = arcpy.Describe(inraster)
        return desc.width, desc.height
    except:
        return getsizePIL(inraster)
        
def getutmzone(lon):
    """takes a wgs84 longitude and returns the utm zone"""
    utmnumber = 30 - int(lon * -1) / 6
    utmname = 'NAD 1983 UTM Zone {0}N'.format(utmnumber)
    return utmname

def createAuxFile(coordinates, utmname, inraster, template):
    """takes corner coordinates and a raster and returns the world file."""
    coordinates['width'], coordinates['height'] = getsize(inraster)
    wkid = WKID_DICT[utmname]
    coordinates['wkid'] = wkid
    utmPrjText = PROJ_DICT[utmname]
    coordinates['prj'] = utmPrjText
    output = template.substitute(coordinates)
    outfile = inraster + '.aux.xml'
    with open(outfile, 'w') as f:
        f.write(output)
        
def findurl(inraster):
    """takes a path to a raster and returns the url for the metadata"""
    # this could be a good function to read in the web data and tell 
    # us if the url correct and try other urls if the first on that is made doesnt work
    urlTemplate = 'http://earthexplorer.usgs.gov/metadata/{0}/{1}'
    basepath, filename = os.path.split(inraster)
    basefilename, extension = os.path.splitext(filename)
    upperbasefilename = basefilename.upper()
    if 'NAPP' in upperbasefilename:
        metadatadir = '4662'
    elif 'NHAP' in upperbasefilename:
        metadatadir = '4663'
    elif upperbasefilename[:2] == 'DS':
        metadatadir = '1051'
    else:
        metadatadir = '4660'
        if upperbasefilename[:2] != 'AR':
            upperbasefilename = 'AR' + upperbasefilename
    url = urlTemplate.format(metadatadir, upperbasefilename)
    return url
    
def createpyramids(inraster):
    """although this is a one liner, it could maybe use some customization"""
    arcpy.BuildPyramids_management(inraster)
    return True
    
def main():
    """"""
    outpath = sys.argv[1]
    inraster = sys.argv[2]
    templatefile = r'J:\GIS_Data\Working-MikeM\template.jpg.aux.xml' #sys.argv[3]
    with open(templatefile) as f:
        text = f.read()
        template = string.Template(text)
    url = findurl(inraster)
    alldata = readmetadatatable(url)
    # this could be dumped into the geojson properties or attributes or whatever they call it in geojson
    field_data = filterdata(alldata, FIELDS)
    coordinates = readcoordinatestable(alldata)
    outbasepath, outfile = os.path.split(outpath)
    outfilename, outfileextension = os.path.splitext(outfile)
    utmcoords, utmname = writeshapefile(coordinates, outpath, field_data)
    createAuxFile(utmcoords, utmname, inraster, template)
    createpyramids(inraster)
    print True

if __name__ == '__main__':
    main()
