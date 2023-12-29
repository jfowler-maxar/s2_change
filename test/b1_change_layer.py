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
out_name = f'{gran}_b{bnum}_ch_v2.tif'
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
mask_nan = np.where(arr_ts<=-9999,0,chang)

#going to try to do focal avg, to remove single pixels
#geoprocessing with python textbook pg 251
def make_slices(data,win_size):
    '''return a list of slices given a window size.
    data - 2d array to get slices from
    win_size - tuple of (rows,colums) for the moving window
    '''
    rows = data.shape[0] - win_size[0] + 1
    cols = data.shape[1] - win_size[1] + 1
    slices = []
    for i in range(win_size[0]):
        for j in range(win_size[1]):
            slices.append(data[i:rows+i, j:cols+j])
    return slices

slices = make_slices(mask_nan,(3,3))
stacked_data = np.dstack(slices)

rows, cols = ysize, xsize
out_data = np.ones((rows,cols),np.int16)
#out_data[1:-1, 1:-1] = np.mean(stacked_data,2)
out_data[1:-1, 1:-1] = np.mean(stacked_data,2)

dst_band.WriteArray(out_data)
