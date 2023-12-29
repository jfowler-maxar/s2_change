import os
from os.path import *
from osgeo import gdal
import numpy as np

work_dir = r'E:\work\change_detect_solo'
gran = "T18SUJ"
gran_dir = join(work_dir, gran)
chang_dir = join(gran_dir, 'change')

bnum = '1'
ts_std = join(chang_dir,f'{gran}_b{bnum}_stacktempslope_std.tif')
date_num = join(chang_dir,f'{gran}_b{bnum}_date_num.tif')
if not exists(ts_std):
    print(f'{ts_std} DNE')
    exit(5)
if not exists(date_num):
    print(f'{date_num} DNE')
    exit(6)

#open files
ds_ts = gdal.Open(ts_std)
ds_dn = gdal.Open(date_num)
srs_prj = ds_ts.GetProjection()
geoTransform = ds_ts.GetGeoTransform()
xsize = ds_ts.RasterXSize
ysize = ds_ts.RasterYSize
num_bands = ds_ts.RasterCount

#setup output
out_name = f'{gran}_b{bnum}_ch.tif'
output_path = join(chang_dir, out_name)
drv = gdal.GetDriverByName("GTiff")
dst_ds = drv.Create(output_path,
                    xsize,
                    ysize,
                    1,
                    gdal.GDT_Byte,
                    )
dst_ds.SetGeoTransform(geoTransform)
dst_ds.SetProjection(srs_prj)
dst_band = dst_ds.GetRasterBand(1)

arr_ts = ds_ts.GetRasterBand(1).ReadAsArray().astype('float32')
arr_dn = ds_dn.GetRasterBand(1).ReadAsArray().astype('float32')
ds_ts = None
ds_dn = None

#where tempslope_std >= |std|, keep date_num, else 0
chang = np.where(np.absolute(arr_ts)>=3,arr_dn,0)
mask_nan = np.where(arr_ts==-9999,0,chang)
dst_band.WriteArray(mask_nan)
