import os
from os.path import *
from osgeo import gdal
import numpy as np

work_dir = r"E:\work\change_detect_solo"
gran = "T18SUJ"
gran_dir = join(work_dir,gran)
time_series_dir = join(gran_dir,'time_series')

if os.path.exists(time_series_dir) == False:
    os.mkdir(time_series_dir)

#take all the various indicies and stack them with gdalbuildvrt
#indicies are in month dir's
#initialize lists
msavi_list= []
ndbi_list= []
ndsi_list= []
ndvi_list= []
ndwi_list= []

for month in os.listdir(gran_dir):
    if len(month) == 6 and month.startswith('2'):
        l1c_dir = join(gran_dir, month, 'MSIL1C')
        l2a_dir = join(gran_dir, month, 'MSIL2A')
        gran_month = gran + "_" + month
        for tif in os.listdir(join(gran_dir,month)):
            if tif.endswith('msavi.tif'):
                msavi_list.append(join(gran_dir,month,tif))
            elif tif.endswith('ndbi.tif'):
                ndbi_list.append(join(gran_dir,month,tif))
            elif tif.endswith('ndsi.tif'):
                ndsi_list.append(join(gran_dir,month,tif))
            elif tif.endswith('ndvi.tif'):
                ndvi_list.append(join(gran_dir,month,tif))
            elif tif.endswith('ndwi.tif'):
                ndwi_list.append(join(gran_dir,month,tif))
print('Done looping through months and creating lists')
#just to make sure in old->new order
msavi_list.sort()
ndbi_list.sort()
ndsi_list.sort()
ndvi_list.sort()
ndwi_list.sort()

msavi_vrt = join(time_series_dir,gran+'_msavi_stack.vrt')
ndbi_vrt = join(time_series_dir,gran+'_ndbi_stack.vrt')
ndsi_vrt = join(time_series_dir,gran+'_ndsi_stack.vrt')
ndvi_vrt = join(time_series_dir,gran+'_ndvi_stack.vrt')
ndwi_vrt = join(time_series_dir,gran+'_ndwi_stack.vrt')

if exists(msavi_vrt) == False:
    print('stacking msavi')
    gdal.BuildVRT(msavi_vrt, msavi_list, separate='separate', resolution='highest')
if exists(ndbi_vrt) == False:
    print('stacking ndbi')
    gdal.BuildVRT(ndbi_vrt, ndbi_list, separate='separate', resolution='highest')
if exists(ndsi_vrt) == False:
    print('stacking ndsi')
    gdal.BuildVRT(ndsi_vrt, ndsi_list, separate='separate', resolution='highest')
if exists(ndvi_vrt) == False:
    print('stacking ndvi')
    gdal.BuildVRT(ndvi_vrt, ndvi_list, separate='separate', resolution='highest')
if exists(ndwi_vrt) == False:
    print('stacking ndwi')
    gdal.BuildVRT(ndwi_vrt, ndwi_list, separate='separate', resolution='highest')
print('all done!')