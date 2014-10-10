import sys
import os
import arcpy
from collections import OrderedDict
from read_metadata import getutmzone
arcpy.env.overwriteOutput = True
wgs84 = arcpy.SpatialReference('WGS 1984')
# some basic wor
INCHESPERMETER = 39.3701
INCHESPERFOOT = 12
QUARTER_MILE_IN_METERS = 402.336

# add a coment

def spatialCursor(targetLayer, inFeature, relationship='intersect',fields=['Filename']):
    """takes a polygon layer and returns the values for the fields that relate with the inFeature"""
    # make a feature layer so we can select be location
    arcpy.MakeFeatureLayer_management(targetLayer, "TEMP_LAYER")
    # do the select by location to find all raster layer footprints that overlap the inFeature
    arcpy.SelectLayerByLocation_management("TEMP_LAYER", relationship, inFeature)
    # start up a searchCursor so we can grab the filenames
    cur = arcpy.da.SearchCursor("TEMP_LAYER", fields)
    # create a blank list
    mylist=[]
    # loop through each row of the table
    for r in cur:
        mylist.append(r)
    # clean up by doing some deletes
    if 'r' in vars().keys():
        del r
    del cur
    arcpy.Delete_management("TEMP_LAYER")
    # and return the list of filenames
    return mylist

def shiftExtents(clipExtent, imageExtent):
    """basic function to shift clipextents to remain the same size but inside of another extent"""
    # logically this is a flawed function
    # it assumes that the imageExtent is bigger than the crop box
    # this should be its own class to deal with bbox logic
    # it could allow for some set like operations
    # and basic shifts
    #comments start for real now
    #############
    # grab the length and width, arc has functions for this that i saw in the documentation
    length = clipExtent.XMax - clipExtent.XMin
    width = clipExtent.YMax - clipExtent.YMin
    # create a blank dict because i am not sure if we can write in extent objects
    # something to look into though
    outExtent = {}
    # if the top of the clipextent is higher than the top of the image move the clipbox down
    if clipExtent.XMax > imageExtent.XMax:
        outExtent['XMax'] = imageExtent.XMax
        outExtent['XMin'] = imageExtent.XMax - length
    # else if the top of the clipextent is lower move the whole thing up
    elif clipExtent.XMin < imageExtent.XMin:
        outExtent['XMin'] = imageExtent.XMin
        outExtent['XMax'] = imageExtent.XMin + length
    # if neither case from above is true there are no problems leave clip box where it was
    else:
        outExtent['XMin'] = clipExtent.XMin
        outExtent['XMax'] = clipExtent.XMax
    # same logic for Y as the above block
    if clipExtent.YMax > imageExtent.YMax:
        outExtent['YMax'] = imageExtent.YMax
        outExtent['YMin'] = imageExtent.YMax - width
    elif clipExtent.YMin < imageExtent.YMin:
        outExtent['YMin'] = imageExtent.YMin
        outExtent['YMax'] = imageExtent.YMin + width
    else:
        outExtent['YMin'] = clipExtent.YMin
        outExtent['YMax'] = clipExtent.YMax
    print outExtent
    return arcpy.Extent(**outExtent)

def geomListToExtent(geomlist):
    """takes a list of arc geometry objects and returns the extent"""
    extents = []
    # make a blank arcpy extent object to fill up later
    outextent = arcpy.Extent()
    # loop through each geometry and grab its extent
    for geom in geomlist:
        extents.append(geom.extent)
    # is there a better way to get the min and max all at once?
    outextent.XMax = max(x.XMax for x in extents)
    outextent.XMin = min(x.XMin for x in extents)
    outextent.YMax = max(x.YMax for x in extents)
    outextent.YMin = min(x.YMin for x in extents)
    return outextent

def geomListToCentroid(geomlist):
    """takes a geometry list and finds the centroid"""
    # get the extent for the whole geomList
    extent = geomListToExtent(geomlist)
    # grab the middle of that extent
    xCentroid = 0.5 * (extent.XMin + extent.XMax)
    yCentroid = 0.5 * (extent.YMin + extent.YMax)
    # and return it
    return xCentroid, yCentroid

def extentToArcPolygon(extent):
    """takes an arcpy extent and creates an arcpy polygon"""
    # blank array and point
    ar = arcpy.Array()
    ar.add(extent.upperLeft)
    ar.add(extent.upperRight)
    ar.add(extent.lowerRight)
    ar.add(extent.lowerLeft)
    ar.add(extent.upperLeft)
    return arcpy.Polygon(ar, extent.spatialReference)

# this function is very similar to findRasters so we should merge them where possible
def findIntersecting(geomlist, otherLayer=r'C:\Workspace\topo_work\topos.gdb\topos_7point5_minute_spatialjoin', relationship="WITHIN", search_radius=".25 Miles", fields=['Id']):
    """takes a geometry list and returns values for the fields as a list of lists from the otherLayer that relate spatially with the relationship.
    search_radius will be used only for relationships that use it like within"""
    # the upper part here is to make a quick selection before making a feature layer which can be slow with bigger shapefiles
    # not sure if this specific of an approach is a good idea, but it can be removed anyway and skip down to the MakeFeatureLayer clause later if its not needed
    # make the extent
    extent = geomListToExtent(geomlist)
    # turn it into a polygon
    poly = extentToArcPolygon(extent)
    # find the portion of the otherLayer that touches that extent
    intersectedGrid = arcpy.SpatialJoin_analysis(otherLayer, poly, r'C:\temp2\temp_grid.shp', '','KEEP_COMMON', match_option=relationship, search_radius=search_radius)
    # turn that into a feature layer
    arcpy.MakeFeatureLayer_management(intersectedGrid, 'TEMP_LAYER')
    for geom in geomlist:
        arcpy.SelectLayerByLocation_management('TEMP_LAYER', relationship, geom, search_distance=search_radius, selection_type="ADD_TO_SELECTION")
    cur = arcpy.SearchCursor("TEMP_LAYER")
    outlist = []
    for r in cur:
        outlist.append([r.getValue(x) for x in fields])
    # delete to clean up some trash
    arcpy.Delete_management("TEMP_LAYER")
    arcpy.Delete_management(intersectedGrid)
    return outlist

def findOrder(orderNumber, queryField="Orders", buffer_dist=QUARTER_MILE_IN_METERS, inFeatures=[r'J:\GIS_Data\HIGCore\Orders.gdb\sitePy', r'J:\GIS_Data\HIGCore\Orders.gdb\sitePt', r'J:\GIS_Data\HIGCore\Orders.gdb\siteLn']):
    """this function takes an order number and returns a python list of all of the shapes that we have for it"""
    # create a blank list
    outlist = []
    # loop through each feature
    for feat in inFeatures:
        # select all features where the queryField equals the orderNumber
        geom = arcpy.Select_analysis(feat, arcpy.Geometry(), """ "{}"= '{}' """.format(queryField, orderNumber))
        # add each list of features to the list (unlike append this makes a flat list)
        outlist += geom
    return outlist

def selectTopos(orderNumber, inFeature=r'J:\GIS_Data\HIGCore\Orders.gdb\sitePy', outdir=r'C:\temp\topoCrops', topoImport=r'C:\Workspace\topo_work\topos.gdb\topos_7point5_minute_spatialjoin',grid=r'C:\Workspace\topo_work\topos.gdb\eighth_degree_grid'):
    """takes an infeature and uses a 7.5 minute grid to return the topos that should be used.
    if the Feature is close to the edge is a grid it will use shiftExtents to shift it close to the edge"""
    # make the basic cropBox
    # if it has a length of two we assume it is a lat lon pair and create our geom for that
    if len(orderNumber)== 2:
        mapDoc = MapDocument(scale=24000, centroid=orderNumber)
        poly = mapDoc.createArcPolygon()
        inFeature = arcpy.PointGeometry(arcpy.Point(X=orderNumber[1],Y=orderNumber[0]), wgs84)
    # otherwise it is probably an order number
    # maybe we should assert that it starts with a 1, has a length between 7 and 8, is a string, or something else
    else:
        poly = createCropBoxTopo(inFeature, orderNumber)
        # select the input feature and save it as a variable
        inFeature = arcpy.Select_analysis(inFeature, r'C:\temp2\temp_feature.shp', """ "Orders"= '{}' """.format(orderNumber))[0]
    # buffer that feature by one quarter mile
    buffered = arcpy.Buffer_analysis(inFeature, r'C:\temp2\temp_feature_buffer.shp', '{} meters'.format(QUARTER_MILE_IN_METERS))
    # find the portions of the grid that intersect the buffered layer
    intersectedGrid = arcpy.SpatialJoin_analysis(grid, buffered, r'C:\temp2\temp_grid.shp', '','KEEP_COMMON')
    # start a search cursor on the grid sections that touch the buffered layer
    cur = arcpy.SearchCursor(intersectedGrid)
    for r in cur:
        # grab the centroid for the current grid
        cellCentroid = r.SHAPE.centroid
        # find out what the utmzone is for the centroid
        utmzonestr = getutmzone(cellCentroid.X)
        # turn it into a spatialReference object
        utmzone = arcpy.SpatialReference(utmzonestr)
        # grab the extent of the 7.5 minute cell
        cellExtent = r.SHAPE.extent.projectAs(utmzone)
        # shift the crop box to match the cell
        cellBoundPoly = shiftExtents(poly.projectAs(utmzone).extent, cellExtent)
        # all garbage to turn the extent into a rectangle
        # so to get around this we need to make it so that clipByPoly can take an extent or polygon and not just a polygon
        centerOfCellBoundPoly = (cellBoundPoly.XMax - (cellBoundPoly.XMax - cellBoundPoly.XMin)/2, cellBoundPoly.YMax - (cellBoundPoly.YMax - cellBoundPoly.YMin)/2)
        point = arcpy.PointGeometry(arcpy.Point(X=centerOfCellBoundPoly[0],Y=centerOfCellBoundPoly[1]), utmzone).projectAs(wgs84)
        mapDoc = MapDocument(scale=24000, centroid=(point.firstPoint.Y,point.firstPoint.X))
        cellBoundPoly = mapDoc.createArcPolygon()
        # GARBAGE ENDS HERE
        # grab the oid
        oid = r.id
        # which allows us to select the rasters that touch that grid
        rasterCur = arcpy.SearchCursor(topoImport,""""Id"={}""".format(oid))
        # loop through those rasters that belong to that grid
        for rr in rasterCur:
            # grab the filename
            topoPath = rr.Filename
            # and feed all the information to clipByPoly function
            clipByPoly(cellBoundPoly, topoPath, outdir, topo=True)
        # there will not always be topos for each grid so we need to use caution when deleting the rr
        if 'rr' in vars().keys():
            del rr
        del rasterCur
    del r, cur
    # delete the temp files
    # some of these can be handled as variables which might save some time, code, and effort
    arcpy.Delete_management(intersectedGrid)
    arcpy.Delete_management(buffered)
    arcpy.Delete_management(inFeature)

def cropBothScales(orderNumber,inFeature=r'J:\GIS_Data\HIGCore\Orders.gdb\sitePy', outdir=r'C:\temp\topoCrops'):
    """calls selectTopos on both 7.5 and 15 minute scales"""
    # with the presets it works on the 7.5 minute grid
    selectTopos(orderNumber, inFeature=inFeature, outdir=outdir)
    # feed the files to it so it runs 15 minute
    selectTopos(orderNumber, topoImport=r'C:\Workspace\topo_work\topos.gdb\topos_15_minute_SpatialJoin', grid=r'C:\Workspace\topo_work\topos.gdb\quarter_degree_grid', inFeature=inFeature, outdir=outdir)
    
def clipByPoly(inPoly, inraster, outdir, topo=False):
    """takes a polygon and clips the inraster to its extent and places output in the outdir"""
    # get the raster description
    try:
        rasterDesc = arcpy.Describe(inraster)
    except Exception as e:
        print e, inraster, 'here'
        return None
    # so we can get the spatialReference of the raster
    rasterSpref = rasterDesc.spatialReference
    # and also the extent of the raster
    rasterExtent = rasterDesc.extent.projectAs(inPoly.spatialReference)
    # if it is a topo
    if topo:
        # then we use the extent without a shift because we know it is good already
        rawutmextent = inPoly.extent
    # otherwise it is for a photo or something else and we dont know that the extent is already matched up
    else:
        # use the shiftExtents function to move the clip extent to be within the raster extent
        rawutmextent = shiftExtents(inPoly.extent, rasterExtent)
    # format the extent object for clipping

    utmextent = ' '.join(map(str,(rawutmextent.XMin, rawutmextent.YMin,rawutmextent.XMax, rawutmextent.YMax)))
    # project the clip extent into the spatialReference of the raster
    rawextent = inPoly.projectAs(rasterSpref).extent
    # and reformat that as well
    extent = ' '.join(map(str,(rawextent.XMin, rawextent.YMin,rawextent.XMax, rawextent.YMax)))
    if rasterExtent.disjoint(extentToArcPolygon(rawutmextent)):
        print 'this is stupid'
        return None

    # create the output name
    # note that we are using tif so this actually works
    outName = os.path.join(outdir, os.path.split(inraster)[1][:-4] + '.tif')
    # do the initial clip to get the potion of the raster that we need
    arcpy.Clip_management(inraster, extent, outName, "", "", 'NONE')
    # if the raster spatial reference is the same as the output we can exit the function right now
    if rasterSpref == inPoly.spatialReference:
        return True
    # create a name for a temp file
    reprojectName = outName[:-4] + 'reproject' + outName[-4:]
    # this part can fail so we put it in a try clause
    # seems like most of the failures were caused by a lock, so these are not a huge issue but should still be in the try block
    try:
        # project the clipped raster into the correct UTM
        arcpy.ProjectRaster_management(outName, reprojectName, inPoly)
        # delete the original clip
        arcpy.Delete_management(outName)
        # reclip the reprojected raster
        arcpy.Clip_management(reprojectName ,utmextent, outName, "", "", 'NONE')
        # and delete the reprojected unclipped raster
        arcpy.Delete_management(reprojectName)
    except Exception as e:
        print e, outName
    return True
    
def createCropBoxTopo(infeature, orderNumber,scale=24000):
    """creates a polygon based off of the order layer with presets for topo. scale is parameter to make it more usable for other shit."""
    # grab the centroid from the order table
    # note that this is flawed because we can have orders that have many rows
    # makes me think that we should do a dissolve on order number or something
    centroid = arcpy.Select_analysis(infeature, arcpy.Geometry(), """ "Orders"= '{}' """.format(orderNumber))[0].centroid
    # flip the fucking point because of fucking arc
    centroid = (centroid.Y,centroid.X)
    # create a MapDocument class
    mapDoc = MapDocument(scale=scale, centroid=centroid)
    # which allows us to create a polygon
    poly = mapDoc.createArcPolygon()
    return poly

def createClipsTopo(inFeatureOrderNumber, inFeature=r'J:\GIS_Data\HIGCore\Orders.gdb\siteLn', rasterLayer=r'C:\HIGCore\HIGCore.gdb\TopoImport', relationship='intersect', outdir=r'C:\temp\topoCrops'):
    """"""
    # create a polygon for the orderNumber
    poly = createCropBoxTopo(inFeature, inFeatureOrderNumber)
    # below is generic logic not for our order layers that i will save in this comment in case i want it in the future
    # poly = arcpy.Select_analysis(inFeature, arcpy.Geometry(), """ "NAME"= '{}' """.format(inFeatureOrderNumber))[0]
    # use the findRasters function to find all rasters that spatial relate with the relationship given to the polygon
    rasters = findRasters(poly, rasterLayer, relationship)
    # loop through each raster and clip them into the output folder
    for raster in rasters:
        clipByPoly(poly, raster, outdir)

def createClipsPhotos(inFeatureOrderNumber, scale=6000, inFeature=r'J:\GIS_Data\HIGCore\Orders.gdb\siteLn', rasterLayer=r'C:\HIGCore\HIGCore.gdb\CountyMosaicImport', relationship='intersect', outdir=r'C:\temp\topoCrops'):
    """specialized function with the presets for photos"""
    if len(inFeatureOrderNumber) != 2:
        poly = createCropBoxTopo(inFeature, inFeatureOrderNumber,scale=scale)
    elif len(inFeatureOrderNumber) == 2:
        mapDoc = MapDocument(scale=scale, centroid=inFeatureOrderNumber)
        poly = mapDoc.createArcPolygon()
    rasters = findRasters(poly, rasterLayer, relationship)
    for raster in rasters:
        clipByPoly(poly, raster[0], outdir)

def createAllClipsPhotos(inFeatureOrderNumber, outdir=r'C:\temp\topoCrops',inFeature=r'J:\GIS_Data\HIGCore\Orders.gdb\sitePy'):
    """specialized function with the presets for the 3 photo layers that we usually use for jobs"""
    # notice that when we call this on county and project which are single frame we only are looking for photos that contain the crop polygon
    createClipsPhotos(inFeatureOrderNumber, scale=30000, rasterLayer=r'C:\HIGCore\HIGCore.gdb\CountyAndProjectImport',relationship='contains',outdir=outdir,inFeature=inFeature)
    # we may need to look up image analyst commands so we can merge doqqs when we are on the edge 
    createClipsPhotos(inFeatureOrderNumber, scale=30000, rasterLayer=r'C:\HIGCore\HIGCore.gdb\DOQQImport',outdir=outdir,inFeature=inFeature)
    # with all the normal presets if does the county mosaics
    createClipsPhotos(inFeatureOrderNumber, scale=30000, outdir=outdir,inFeature=inFeature)

class LinearScale:
    """"""
    def __init__(self, domain=[0,1], outrange=[0,1], limit=False):
        """a basic linear scale that allows converting from a domain to a range"""
        if type(domain) == int:
            domain = [0, domain]
        if type(outrange) == int:
            outrange = [0, outrange]
        self.domain = domain
        self.outrange = outrange
        self.domainExtent = domain[1] - domain[0]
        self.outrangeExtent = outrange[1] - outrange[0]
        self.limit = limit
    
    def get(self, inval):
        """takes a value and converts it scaled to the outrange """
        if self.limit:
            assert self.domain[0] < inval < self.domain[1], 'needs to be inside the domain when limit is set to true'
        indiff = float(inval - self.domain[0])
        inz = indiff / self.domainExtent
        outz = inz * self.outrangeExtent
        outval = outz + self.outrange[0]
        return outval
        
    def invert(self):
        """returns a new scale that is the inverse of the current scale"""
        return LinearScale(self.outrange, self.domain, self.limit)
        
class Domain:
    """basic domain object with a high and low value, name, and a boolean for if its a limited scale or not"""
    def __init__(self, name, low, high, limit):
        """"""
        self.name = name
        self.low = low
        self.high = high
        self.limit = limit
        self.extent = high - low
        
    def __str__(self):
        """"""
        basetext =  'Domain object named {name} with low val: {low}, high val: {high}, and limit:{limit}'
        return basetext.format(self.__dict__)
        
class ManyWayLinearScale:
    """"""
    def __init__(self, domains):
        """"""
        self.domains = [x.name for x in domains]
        for domain in domains:
            setattr(self, domain.name, domain)
        
    def __str__(self):
        """"""
        return 'ManyWayLinearScale with domains {}'.format(', '.join(map(str,domains)))
        
    def convert(self, inval, inDomain, outDomain):
        """"""
        if inDomain.limit or outDomain.limit:
            assert inDomain.low <= inval < inDomain.high, 'needs to be inside indomain'
        indiff = float(inval - inDomain.low)
        inz = indiff / indomain.extent
        outz = inz * outDomain.extent
        outval = outz + outDomain.low
        return outval

class ScaleTwoDimensions(object):
    """"""
    def __init__(self, domainX=[0,1], domainY=[0,1], outrangeX=[0,1], outrangeY=[0,1], limit=False):
        """"""
        self.scaleX = LinearScale(domainX, outrangeX, limit)
        self.scaleY = LinearScale(domainY, outrangeY, limit)
        
    def get(self, invalX, invalY):
        """"""
        x = self.scaleX.get(invalX)
        y = self.scaleY.get(invalY)
        return (x, y)
        
    def invert(self):
        """"""
        return ScaleTwoDimensions(self.domainY, self.domainX, self.outrangeY, self.outrangeX, self.limit)

class MapDocument(ScaleTwoDimensions):
    """"""
    def __init__(self, width=8, height=9, scale=6000, centroid=[0, 0], spatialRef=None):
        """takes dimensions of a map document in inches, the scale, corner in localUtm, and spatialRef for that corner.
        this function creates a mike mommsen MapDocument, which should allow for some nice cropping options.
        the cornerType  starts with N|S|C for if the corner is north, south, or central.
        the second char of cornertype is E|W|C for east, west, central."""
        # update these comments to reflect the latest changes that i have made
        self.width = width
        self.height = height
        self.scale = scale
        meterscale = scale / INCHESPERMETER
        self.meterwidth = meterwidth = width * meterscale
        self.meterheight = meterheight = height * meterscale
        if spatialRef:
            self.spatialRef=arcpy.SpatialReference(spatialRef)
        else:
            self.setSpatialReference(centroid)
        self.centroid = centroid
        utmCentroid = arcpy.PointGeometry(arcpy.Point(X=centroid[1],Y=centroid[0]), wgs84).projectAs(self.spatialRef)
        x = (utmCentroid.firstPoint.X, utmCentroid.firstPoint.Y)
        print x
        rightedge = x[0] - meterwidth /2
        topedge = x[1] + meterheight/2
        leftedge = x[0] + meterwidth/2
        bottomedge = x[1] - meterheight/2
        self.corners = OrderedDict([('nw', [topedge,rightedge]), ('ne', [topedge,leftedge]), ('se', [bottomedge,leftedge]), ('sw', [bottomedge,rightedge])])
        super(self.__class__, self).__init__(width, height, [x[0],leftedge],[x[1], bottomedge])# look up the syntax for this shit - its pretty cool though

    def setSpatialReference(self,point):
        """"""
        # if the user did not define a spatialReference
        utmzone = getutmzone(point[1])
        self.spatialRef = arcpy.SpatialReference(utmzone)
            
    def createArcPolygon(self,outshp=None):
        """"""
        ar = arcpy.Array()
        pnt = arcpy.Point()
        for corner in self.corners.values():
            pnt.X = corner[1]
            pnt.Y = corner[0]
            ar.append(pnt)
        poly = arcpy.Polygon(ar, self.spatialRef)
        if outshp:
            cur = arcpy.InsertCursor(outshp)
            r = cur.newRow()
            r.setValue("shape", poly)
            cur.insertRow(r)
            del r, cur
        else:
            return poly

def changeCorners(inPoint, mapwidth, mapheight, scale, inPointCorner, outPointCorner):
    """"""
    surfacewidth = mapwidth * scale
    surfaceheight = mapheight * scale
    if inPointCorner == 'C':
        pass
    elif inPointCorner == 'NW':
        pass
    elif inPointCorner == 'NE':
        pass
    elif inPointCorner == 'SE':
        pass
    elif inPointCorner == 'SW':
        pass

def GARBAGE_PULLED_FROM_INIT():
    # this section allows corner changing - maybe seperate function that is called by __init__
    # one more problem is that we need to know the utm zone to know other conversions
    if cornertype[0] ==  'N':
        pass
    elif cornertype[0] == 'S':
        corner[0] -= meterwidth
    elif cornertype[0] == 'C':
        corner[0] -= (meterwidth / 2)
    else:
        print 'unrecognized cornertype'
    if cornertype[1] ==  'W':
        pass
    elif cornertype[1] == 'E':
        corner[1] += meterheight
    elif cornertype[1] == 'C':
        corner[1] += (meterheight / 2)
    else:
        print 'unrecognized cornertype'
    # section ends here

def main():
    if len(sys.argv) == 2:
        arg1 = sys.argv[1]
        arg2 = sys.argv[2]
    else:
        pass

if __name__ == '__main__':
    main()
