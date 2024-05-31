import os
from os.path import *
from osgeo import gdal
import numpy as np

work_dir = r'E:\work\change_detect_solo'
gran = "T18SUJ"
gran_dir = join(work_dir, gran)
chang_dir = join(gran_dir, 'change')
temp_slope_dir = join(gran_dir,'temp_slope')

bnum = '1'
ts = join(temp_slope_dir, f'{gran}_b{bnum}_stacktempslope.tif')
ts_std = join(chang_dir,f'{gran}_b{bnum}_tempslope_std_focal_filter.tif')
date_num = join(chang_dir,f'{gran}_b{bnum}_date_num_focal_filter.tif')
if not exists(ts_std):
    print(f'{ts_std} DNE')
    exit(5)
if not exists(date_num):
    print(f'{date_num} DNE')
    exit(6)
if not exists(ts):
    print(f'{ts} DNE')
    exit(7)

#open files
ds_tempslope = gdal.Open(ts)
ds_ts_std = gdal.Open(ts_std)
ds_dn = gdal.Open(date_num)
srs_prj = ds_ts_std.GetProjection()
geoTransform = ds_ts_std.GetGeoTransform()
xsize = ds_ts_std.RasterXSize
ysize = ds_ts_std.RasterYSize
num_bands = ds_ts_std.RasterCount

#setup output
out_name = f'{gran}_b{bnum}_ch_tmp.tif'#tmp till goes through sieve
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

arr_ts_std = ds_ts_std.GetRasterBand(1).ReadAsArray().astype('float32')
arr_dn = ds_dn.GetRasterBand(1).ReadAsArray().astype('float32')
arr_ts = ds_tempslope.GetRasterBand(1).ReadAsArray().astype('float32')
ds_ts_std = None
ds_dn = None
ds_tempslope = None

#where ts_std >= |std thresh| OR ds_tempslope >= |tempslope thresh|
chang = np.where(np.logical_or(np.absolute(arr_ts_std)>=5, np.absolute(arr_ts)>=75),arr_dn,0) #was at 3 befor
mask_nan = np.where(arr_ts_std<0,0,chang)

dst_band.WriteArray(mask_nan)
