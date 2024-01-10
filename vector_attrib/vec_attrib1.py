import os
from os.path import *
#from osgeo import gdal, ogr,osr
import numpy as np
from rasterstats import zonal_stats
#import rasterio as rio
import geopandas as gpd
import pandas as pd

work_dir = r'E:\work\change_detect_solo'
gran = "T20LMR"
gran_dir = join(work_dir, gran)
change_dir = join(gran_dir,'change')
time_stats_dir = join(gran_dir,'time_stats')
vec_dir = join(gran_dir,'vec')

bnum = '1'
in_name = f'{gran}_b{bnum}_ch_tmp.shp'
#in_name = r"E:\work\change_detect_solo\T20LMR\vec\test_in.shp" #testing smaller subset
in_shp = join(vec_dir, in_name)

out_test = f'{gran}_b{bnum}_ch_final.shp'
#out_test = r"E:\work\change_detect_solo\T20LMR\vec\test_out.shp"
out_shp = join(vec_dir, out_test)


#attributes to start out with: change date, tempslope_std, veg, water
#tempslope_std
ts_std_file = join(change_dir,f'{gran}_b{bnum}_stacktempslope_std.tif')
veg_std_file = join(time_stats_dir,f'{gran}_ndvi_std.tif')#veg_std to find osciallating veg(ag/decidious)
veg_mean_file = join(time_stats_dir,f'{gran}_ndvi_mean.tif')#veg_mean for now to get if vegated change
water_std_file = join(time_stats_dir,f'{gran}_ndwi_std.tif')#water_std to find osciallating water
#std_tempslope uses ndwi_mean to mask out water

#get change dates
month_lst = []
for month in os.listdir(gran_dir):
    if len(month) == 6 and month.startswith('2'):
        month_lst.append(month)
print(month_lst)
#month_lst index == changedate for in_shape.date attrib

in_gpd = gpd.read_file(in_shp)
print(in_gpd.head())
#add new column
in_gpd['month'] = in_gpd['date']
#in_gpd['changedate'] = pd.cut(x=in_gpd.date,bins = date_lst,labels = month_lst)
for i in range(len(month_lst)):
    print(f'replacing {i} with {month_lst[i]}')
    print(type(i))
    #j = int(month_lst[i])
    #in_gpd['month'] = pd.DataFrame.replace(i,j)
    in_gpd['month'] = np.where(in_gpd['date'] == i,month_lst[i],in_gpd['month'])

in_gpd = gpd.GeoDataFrame.drop(in_gpd,columns=['date'])#remove change number

#create fields
print('working on adding slope std')
in_gpd['slope_std'] = pd.DataFrame(zonal_stats(vectors = in_gpd['geometry'],raster = ts_std_file,stats=['majority']))
print('working on adding veg')
in_gpd['veg_mean'] = pd.DataFrame(zonal_stats(vectors = in_gpd['geometry'],raster = veg_mean_file,stats=['majority']))
in_gpd['veg_mean'] = np.where(in_gpd['veg_mean'] >= 20,'veg','non-veg')

in_gpd['veg_std'] = pd.DataFrame(zonal_stats(vectors = in_gpd['geometry'],raster = veg_std_file,stats=['majority']))
in_gpd['veg_std'] = np.where(in_gpd['veg_std'] >= 20,'high variation','low variation')

print('working on adding water')#in_gpd['water'] = pd.DataFrame(zonal_stats(vectors = in_gpd['geometry'],raster = water_std_file,stats=['majority']))
in_gpd['water_std'] = pd.DataFrame(zonal_stats(vectors = in_gpd['geometry'],raster = water_std_file,stats=['majority']))
in_gpd['water_std'] = np.where(in_gpd['water_std'] >= 20,'high variation','low variation')

print(f'creating {out_shp}')
in_gpd.to_file(out_shp,driver='ESRI Shapefile')
