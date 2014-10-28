# trying to download some shit
import urllib
import os
import time
import datetime

baseurl = 'http://data.cei.psu.edu/pennpilot/era1960/lackawanna_1960/lackawanna_1960_photos_jpg_800/lackawanna_050459_aqz_2w_38.zip'
templateurl = 'http://data.cei.psu.edu/pennpilot/era{era}/{county}_{era}/{county}_{era}_photos_jpg_800/{county}_{date:%m%d%y}_{project}_{roll}{mission}_{frame}.zip'

class BaseFrame:
    def __init__(self, date, project, roll, mission, frame, county, era='1960',templateurl=templateurl):
        self.era = era
        self.project = project
        self.roll = roll
        self.mission = mission
        self.frame = frame
        self.date = date
        self.county = county
        self.templateurl=templateurl

    def makeUrl(self):
        return self.templateurl.format(**self.__dict__)

    def increaseDate(self, val=1):
        self.date = self.date + datetime.timedelta(val)

    def increaseFrame(self, val=1):
        self.frame += val

    def resetFrame(self):
        self.frame = 1

    def increaseRoll(self, val=1):
        self.roll += val

    def download(self, outdir):
        url = self.makeUrl()
        name = url.split('/')[-1]
        outpath = os.path.join(outdir, name)
        try:
            urllib.urlretrieve(url, outpath)
        except Exception as e:
            print e
        
firstdict = dict(county = 'lackawanna', era='1960', date = datetime.datetime(year=1959, month=5,day=5), roll = '2', frame = '38', project = 'aqz', mission = 'w')
bf = BaseFrame(**firstdict)
print bf.download(r'C:\temp')

