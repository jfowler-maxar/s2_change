import os
import subprocess
from os.path import *
from osgeo import gdal
from osgeo import ogr, gdal
#from zipfile import ZipFile
import shutil

work_dir = r"E:\work\change_detect_solo"
glo30_dir = r"E:\work\dem\glo30"
gran = "T18SUJ"
gran_dir = join(work_dir,gran)
#probably easiest to just take s2_grid vector file, select a granule, then get extents with that

#https://pcjericks.github.io/py-gdalogr-cookbook/vector_layers.html#filter-by-attribute
s2_grid_shp = r"E:\work\s2_grid\Sentinel-2-Shapefile-Index-master\sentinel_2_index_shapefile.shp"
driver = ogr.GetDriverByName('ESRI Shapefile')
dataSource = driver.Open(s2_grid_shp, 0)
layer = dataSource.GetLayer()

layer.SetAttributeFilter("Name = '{}'".format(gran[1:]))
for feature in layer:
    geometry = feature.GetGeometryRef()
    extent = geometry.GetEnvelope()
extent_list = (list(extent))
ns_top = extent_list[3]
ns_bottom = extent_list[2]
ew_left = extent_list[0]
ew_right = extent_list[1]

#print(ns_top, ns_bottom, ew_left, ew_right)
#should probably buffer the dem just in case
ns_top = ns_top+0.01
ns_bottom = ns_bottom-0.01
ew_left = ew_left-0.01
ew_right = ew_right+0.01
#print(ns_top, ns_bottom, ew_left, ew_right)

#next figure out which dem geocells need to be downloaded
#here's an example code of what the aws cmd line should look like
#aws s3 cp
# --no-sign-request
# s3://copernicus-dem-30m/Copernicus_DSM_COG_10_N39_00_W078_00_DEM/
# E:\work\dem\glo30\n39_w078\
# --recursive
# --exclude "*"
# --include "*DEM.tif"

lat1 = int(ns_top)
if lat1 > 0:
    lat1 = "N"+str(lat1)
else:
    lat1 = "S"+str(lat1) #- is the first character in the south
lat2 = int(ns_bottom)
if lat2 > 0:
    lat2 = "N"+str(lat2)
else:
    lat2 = "S"+str(lat2) #- is the first character in the south
long1 = int(ew_left)
if long1 >= 0:
    if long1 < 100:
        long1 = "E0"+str(long1)
    elif long1 >=100:
        long1 = "E" + str(long1)
elif long1 < 0:
    long1 = long1*-1
    if long1 > -100:
        long1 = "W0"+str(long1+1)
    elif long1 <= -100:
        long1 = "W" + str(long1+1)
long2 = int(ew_right)
if long2 >= 0:
    if long2 < 100:
        long2 = "E0"+str(long2)
    elif long2 >=100:
        long2 = "E" + str(long2)
elif long2 < 0:
    long2 = long2*-1
    if long2 > -100:
        long2 = "W0"+str(long2+1)
    elif long2 <= -100:
        long2 = "W" + str(long2+1)
print(lat1,lat2,long1,long2)

#download all glo30
#combo 1, probalby should have done some dictionary stuff...
lat_long = lat1+'_'+long1
lat_long_dir = join(glo30_dir,lat_long)
if os.path.exists(lat_long_dir) == False:
    os.mkdir(lat_long_dir)
if os.path.isfile(join(lat_long_dir,'Copernicus_DSM_COG_10_{}_00_{}_00_DEM.tif'.format(lat1,long1))):
    print('Copernicus_DSM_COG_10_{}_00_{}_00_DEM Already Exists'.format(lat1,long1))
else:
    cmd = r'aws s3 cp --no-sign-request s3://copernicus-dem-30m/Copernicus_DSM_COG_10_{}_00_{}_00_DEM/ E:\work\dem\glo30\{}_{}\ --recursive --exclude "*" --include "*DEM.tif"'.format(lat1,long1,lat1,long1)
    subprocess.run(cmd)
    print(cmd)
#combo 2
lat_long = lat1+'_'+long2
lat_long_dir = join(glo30_dir,lat_long)
if os.path.exists(lat_long_dir) == False:
    os.mkdir(lat_long_dir)
if os.path.isfile(join(lat_long_dir,'Copernicus_DSM_COG_10_{}_00_{}_00_DEM.tif'.format(lat1,long2))):
    print('Copernicus_DSM_COG_10_{}_00_{}_00_DEM Already Exists'.format(lat1,long2))
else:
    cmd = r'aws s3 cp --no-sign-request s3://copernicus-dem-30m/Copernicus_DSM_COG_10_{}_00_{}_00_DEM/ E:\work\dem\glo30\{}_{}\ --recursive --exclude "*" --include "*DEM.tif"'.format(lat1,long2,lat1,long2)
    subprocess.run(cmd)
    #print(cmd)
#combo 3
lat_long = lat2+'_'+long2
lat_long_dir = join(glo30_dir,lat_long)
if os.path.exists(lat_long_dir) == False:
    os.mkdir(lat_long_dir)
if os.path.isfile(join(lat_long_dir,'Copernicus_DSM_COG_10_{}_00_{}_00_DEM.tif'.format(lat2,long2))):
    print('Copernicus_DSM_COG_10_{}_00_{}_00_DEM Already Exists'.format(lat2,long2))
else:
    cmd = r'aws s3 cp --no-sign-request s3://copernicus-dem-30m/Copernicus_DSM_COG_10_{}_00_{}_00_DEM/ E:\work\dem\glo30\{}_{}\ --recursive --exclude "*" --include "*DEM.tif"'.format(lat2,long2,lat2,long2)
    subprocess.run(cmd)
    #print(cmd)
#combo 4
lat_long = lat2+'_'+long1
lat_long_dir = join(glo30_dir,lat_long)
if os.path.exists(lat_long_dir) == False:
    os.mkdir(lat_long_dir)
if os.path.isfile(join(lat_long_dir,'Copernicus_DSM_COG_10_{}_00_{}_00_DEM.tif'.format(lat2,long1))):
    print('Copernicus_DSM_COG_10_{}_00_{}_00_DEM Already Exists'.format(lat2,long1))
else:
    cmd = r'aws s3 cp --no-sign-request s3://copernicus-dem-30m/Copernicus_DSM_COG_10_{}_00_{}_00_DEM/ E:\work\dem\glo30\{}_{}\ --recursive --exclude "*" --include "*DEM.tif"'.format(lat2,long1,lat2,long1)
    #print(cmd)
    subprocess.run(cmd)

#next, mosaic dem's to extent
#drop it in s2_gran folder
#call it something like _dem_buffer.tif
#will have to reproject/cut to actual jp2's extent
#ns_top ns_bottom ew_left ew_right
#lat1, lat2, long1,long2
gran_dem = join(gran_dir,gran+"_glo30_buf.tif")

#this is kinda messy going back and forth but eh idc
lat_long1 = join(glo30_dir,lat1+'_'+long1)
glo_1 = join(lat_long1,'Copernicus_DSM_COG_10_{}_00_{}_00_DEM.tif'.format(lat1,long1))
lat_long2 = join(glo30_dir,lat1+'_'+long2)
glo_2 = join(lat_long2,'Copernicus_DSM_COG_10_{}_00_{}_00_DEM.tif'.format(lat1,long2))
lat_long3 = join(glo30_dir,lat2+'_'+long1)
glo_3 = join(lat_long3,'Copernicus_DSM_COG_10_{}_00_{}_00_DEM.tif'.format(lat2,long1))
lat_long4 = join(glo30_dir,lat2+'_'+long2)
glo_4 = join(lat_long4,'Copernicus_DSM_COG_10_{}_00_{}_00_DEM.tif'.format(lat2,long2))

glo_dems_list = [glo_1, glo_2, glo_3, glo_4]
input_ds = []
for f in glo_dems_list:
    ds = gdal.Open(f)
    input_ds.append(ds)
gdal.Warp(gran_dem,input_ds,
          outputBounds=(ew_left,ns_bottom,ew_right,ns_top),
          format="GTiff",
          outputType=gdal.GDT_Float32
          )