import csv
import sqlite3
import os
import sys
from collections import namedtuple

# create named tuples for some nice loading if that is needed down the road
HistoricalQuads = namedtuple('HistoricalQuads', 'Item_ID,Primary_State,Map_Name,Map_Scale,CurrentYear,Date_On_Map,PR_Year,PI_Year,Aerial_Photo_Year,Datum,Projection,FileName,File_Name,Publishers,Duplicate'.lower().split(','))
topo = namedtuple('topo', 'Series,Version,Cell_ID,Map_Name,Primary_State,Scale,Date_On_Map,Imprint_Year,Woodland_Tint,Visual_Version_Number,Photo_Inspection_Year,Photo_Revision_Year,Aerial_Photo_Year,Edit_Year,Field_Check_Year,Survey_Year,Datum,Projection,Advance,Preliminary,Provisional,Interim,Planimetric,Special_Printing,Special_Map,Shaded_Relief,Orthophoto,Pub_USGS,Pub_Army_Corps_Eng,Pub_Army_Map,Pub_Forest_Serv,Pub_Military_Other,Pub_Reclamation,Pub_War_Dept,Pub_Bur_Land_Mgmt,Pub_Natl_Park_Serv,Pub_Indian_Affairs,Pub_EPA,Pub_Tenn_Valley_Auth,Pub_US_Commerce,Keywords,Map_Language,Scanner_Resolution,Cell_Name,Primary_State_Name,N_Lat,W_Long,S_Lat,E_Long,Link_to_HTMC_Metadata,Download_GeoPDF,View_FGDC_Metadata_XML,View_Thumbnail_Image,Scan_ID,GDA_Item_ID,Create_Date,Byte_Count,Grid_Size'.lower().split(','))
topomaps_replaced_by = namedtuple('topomaps_replaced_by', 'Series,GDA_Item_ID,Replaced_By_ID,Scan_ID,Cell_ID'.lower().split(','))
topoimport = namedtuple('topoimport', 'OBJECTID,Name,Filename,Scale,Year,State,Shape_Length,Shape_Area,centroid_lat,centroid_lon'.lower().split(','))


tables = ['topoimport', 'topomaps_replaced_by', 'topo', 'historicalquads']
os.chdir(r'C:\Workspace\topo_work\topomaps_all')
conn = sqlite3.connect('topo_metadata3.db')
cur = conn.cursor()

# we need to fix the names on the new topos in topoimport
cur.execute('drop index topoimport_name')
conn.commit()
mylist = cur.execute('select rowid, filename, name from topoimport where year > 2008').fetchall()
for rowid, filename, name in mylist:
    if '_OE_' in filename:
        base, end = os.path.split(filename)
        data =  end[3:-20].replace('_',' ')
        cur.execute('update topoimport set name = "{}" where rowid = rowid'.format(data, rowid))
conn.commit()
# and we have to redo the join with these new names
cur.execute('create index topoimport_name on topoimport(name)')
conn.commit()
cur.execute('update topoimport set gda_item_id = (select t.gda_item_id from topo t where t.date_on_map = topoimport.year and t.map_name = topoimport.name and topoimport.state = t.primary_state) where year > 2008')
conn.commit()


###### these are all commands that have been run on the database
## these were commands to get a the item_id to work
#cur.execute('alter table HistoricalQuads add column new_item_id')
#conn.commit()
##cur.execute('update HistoricalQuads set new_item_id = (SELECT t.Replaced_By_ID FROM topomaps_replaced_by t WHERE t.GDA_Item_ID = HistoricalQuads.Item_ID )')
##conn.commit()
##cur.execute('update HistoricalQuads set new_item_id = item_id where new_item_id is null')
##conn.commit()


# this is the query to find the topos in the historic quad layer that dont have valid paths
# there are 81 so we need to look at this in some detail
##ii = cur.execute('select filename, new_item_id from HistoricalQuads')
##for i in ii:
##    if not os.path.exists(i[0]): print i[0], i[1]

###### this is the work the create normalized filepath names in the topoimport
##cur.execute('alter table topoimport add column normfilename')
##conn.commit()
##ii = list(cur.execute('select filename, rowid from topoimport'))
##for filename, rowid in ii:
##    normpath = os.path.normcase(os.path.normpath(filename))
##    if normpath[:2].lower() == 'm:':
##        normpath = r'\\server1\m' + normpath[2:]
##    cur.execute('update topoimport set normfilename = "{}" where rowid = {}'.format(str(normpath), rowid))
##conn.commit()

# we also need to make the ones in historicalquads lowercase to match for a quicker join
##cur.execute('alter table historicalquads add column normfilename')
##conn.commit()
##cur.execute('update historicalquads set normfilename = lower(filename)')
##conn.commit()

# now we need to build indices
##cur.execute('create index topoimport_normfilename on topoimport(normfilename)')
##cur.execute('create index historicalquads_normfilename on historicalquads(normfilename)')
##conn.commit()

# this is too slow ### not anymore with the indices bitch!!!!
#print cur.execute('select count(*) from topoimport t inner join historicalquads h  on t.normfilename=h.normfilename').fetchall()
# >> result = 120914
# now we add the gda key to the ones we can in topoimport, which is 120914 from this operation
#cur.execute('alter table topoimport add column gda_item_id')
#conn.commit()
cur.execute('update topoimport set gda_item_id = null')
cur.execute('update topoimport set gda_item_id = (select h.new_item_id from historicalquads h where h.normfilename = topoimport.normfilename)')
conn.commit()

##cur.execute('create index topoimport_year on topoimport(year)')
##cur.execute('create index topoimport_name on topoimport(name)')
##cur.execute('create index topo_year on topo(date_on_map)')
##cur.execute('create index topo_name on topo(map_name)')
##cur.execute('create index topo_state on topo(primary_state)')
##cur.execute('create index topoimport_state on topoimport(state)')
##conn.commit()
#cur.execute('update topoimport set gda_item_id = (select t.gda_item_id from topo t where t.date_on_map = topoimport.year and t.map_name = topoimport.name and topoimport.state = t.primary_state) where gda_item_id is null')
##conn.commit()
##print cur.execute('select count(*) from topoimport where year > 2008 and gda_item_id is null').fetchone()
###cur.execute('alter table topoimport add column gda_item_id_mix_match')
##conn.commit()
##cur.execute('update topoimport set gda_item_id_mix_match = (select t.gda_item_id from topo t where t.date_on_map >2008 and t.map_name = topoimport.name and topoimport.state = t.primary_state) where gda_item_id is null')
##conn.commit()
##print cur.execute('select count(*) from topoimport where year > 2008 and gda_item_id is null').fetchone()
##
### create the polygon table
##cur.execute('create table polygons as select distinct cell_id, datum, N_Lat, W_Long, S_Lat, E_Long, keywords from topo')
##polys = cur.execute('select * from polygons').fetchall()
##for poly in polys:
##    print poly
##    break




# make the cells database tables
##cur.execute('create table cells_with_keywords as select distinct cell_id, N_Lat, W_Long, S_Lat, E_Long, keywords from topo')
##cur.execute('create table cells as select distinct cell_id, N_Lat, W_Long, S_Lat, E_Long from topo')
##conn.commit()


# we can run the same query on topoimport
# all of the topoimport paths are valid!!!!!!!
##ii = cur.execute('select filename from topoimport limit 100')
##for i in ii:
##    print i





conn.close()

