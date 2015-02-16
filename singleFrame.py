# mike mommsen
# feb 2015

URLTEMPLATE = 'http://earthexplorer.usgs.gov/metadata/{folder}/{usgsname}',

# templates to the usgs entityids
# notive that nhap and napp could maybe be the same
TEMPLATES = dict(
        # method is black and white (b) or color (c)
        # project is 80, 81, 82 etc
        nhap = 'N{method}1{project}{roll:0>4}{frame:0>3}',
        # method 1 for b and w p for cir
        # project is something like nappw or napp
        napp = 'N{method}{project:0>6}{roll:0>5}{frame:0>3}',
        # agency refers to agency dict
        singleframe = 'AR{agency}{project:0>5}{roll:0>3}{frame:0>4}')

# the folders for usgs metadata
FOLDERS = dict(nhap=4663, napp=4662, singleframe=4660)

# list of tuples 
# first entry is the code, second the descriptor
EE_AGENCY_DICT = (
	             ('R', 'NASA-Marshall Space Flight Center'),
                 ('U', 'Urban Area Photography (Homeland Security)'),
                 ('5', 'NASA AMES Research Center'),
                 ('4', 'U.S. Bureau of Land Management'),
                 ('2', 'U.S. Dept of Power & Water Resources'),
                 ('H', 'EROS Miscellaneous'),
                 ('P', 'EROS Acquired'),
                 ('M', 'McDonnell Douglas'),
                 ('L', 'National Park Service'),
                 ('1', 'U.S. Geological Survey'),
                 ('6', 'NASA Johnson Space Center'),
                 ('N', 'U.S. Corps of Engineers'),
                 ('J', 'Federal Emergency Management Agency (FEMA)'),
                 ('Z', 'Hazards-Hurricane Mitch'),
                 ('D', 'NASA-Wallops Island'),
                 ('C', 'U.S. Navy'),
                 ('I', 'NASA Stennis Space Center'),
                 ('B', 'U.S. Air Force'),
                 ('A', 'Army Map Service')
                 )

class CountyMosaic(Photo):
	""""""

	def __init__(self):
		""""""
		Photo.__init__(self, aerialType='countymosaic')
		self.parseBaseName()

	def getShapeFilePath(self):
		"""returns the path to the shapefile corresponding to the countyMosiac"""
		path = os.path.splitext(self)[0] = '.shp'
		if os.path.exists(path):
			self.shapeFilePath = path
		else:
			self.shapeFilePath = raw_input('we could not find the path to the shapefile\
				                             example c:\this\that.shp\
			                                 enter it here: ')
		return self.shapeFilePath

	def getDates(self, geometry):
		"""
		returns a list of datetime objects for photos intersect the geometry

		parameters
		----------
		geometry - arcpy.geometry object
		"""
		if not hasattr(self, 'shapeFilePath'):
			self.getShapeFilePath()
		shapefields = arcpy.ListFields_management(self.shapeFilePath)
		# we need to figure out what the date field is 
		self.dates = [x[0] for x in findRasters(geometry, self.shapeFilePath, fields=['date'])]
		return self.dates

class SingleFrame(Photo):
    """"""

    def __init__(self, fullpath):
    	""""""
        Photo.__init__(self, fullpath, aerialType='singleFrame')
        self.parseBaseName()

class UsgsSingleFrame(SingleFrame):
    """"""

    def __init__(self, fullpath):
        SingleFrame.__init__(self, fullpath)
        self.urltemplate = URLTEMPLATE

    def getPhotoType(self):
        """figures out if a photo is napp, nhap, or other (called singleframe)"""
        if 'napp' in self.filename.lower():
            self.photoType = 'napp'
        elif 'hap' in self.filename.lower():
            self.photoType = 'nhap'
        else:
            self.photoType = 'singleframe'
        self.eeFolder = FOLDERS[self.photoType]
        self.eeTemplate = TEMPLATES[self.photoType]
        return self.photoType

    def getUrl(self):
        """returns the url to metadata for the photo"""
        pass
