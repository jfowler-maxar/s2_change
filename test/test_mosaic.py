import os
from os.path import *
from osgeo import gdal
import numpy as np

work_dir = r'E:\work\change_detect_solo'
gran = "T37RBM"
gran_dir = join(work_dir, gran)
mosaic_dir = join(gran_dir, 'mosaic')
if not exists(mosaic_dir):
    os.mkdir(mosaic_dir)

# test inputs
t_04 = r'E:\work\change_detect_solo\T37RBM\20230427\T37RBM_20230427_6band_masked.tif'
t_09 = r'E:\work\change_detect_solo\T37RBM\20230929\T37RBM_20230929_6band_masked.tif'
t_12 = r'E:\work\change_detect_solo\T37RBM\20231213\T37RBM_20231213_6band_masked.tif'

# just use b1 for now cause fuck it faster for the test

ds_04 = gdal.Open(t_04)
ds_09 = gdal.Open(t_09)
srs_prj = ds_04.GetProjection()
geoTransform = ds_04.GetGeoTransform()
xsize = ds_04.RasterXSize
ysize = ds_04.RasterYSize

tmp1_name = 'tmp1_mosaic_v3.tif'
output_path = join(mosaic_dir, tmp1_name)
# mosaic 1
drv = gdal.GetDriverByName("GTiff")
dst_ds = drv.Create(output_path,
                    xsize,
                    ysize,
                    1,
                    gdal.GDT_Int16,
                    )
dst_ds.SetGeoTransform(geoTransform)
dst_ds.SetProjection(srs_prj)
dst_band = dst_ds.GetRasterBand(1)
# dst_band.SetNoDataValue(-32768)

print('chipping')
block_xsize = 512
block_ysize = 512
minx = geoTransform[0]
miny = geoTransform[3]
step_x = geoTransform[1]
step_y = geoTransform[5]
count_x = 0
count_y = 0

for x in range(0, xsize, block_xsize):
    # print(f'block x: {x}')
    if x + block_xsize < xsize:
        cols = block_xsize
        x_off = minx + (count_x * step_x)
        count_x = count_x + block_xsize
    else:
        cols = xsize - x
        x_off = minx + (count_x * step_x)
        count_x = count_x + x
    count_y = 0
    for y in range(0, ysize, block_ysize):
        print(f'block xy: {x} {y}')
        if y + block_ysize < ysize:
            rows = block_ysize
            y_off = miny + (count_y * step_y)
            count_y = count_y + block_ysize
        else:
            rows = ysize - y
            y_off = miny + (count_y * step_y)
            count_y = count_y + y

        # this is where calculations/data maniuplations happen
        band_04 = ds_04.GetRasterBand(1).ReadAsArray(x, y, cols, rows).astype('float32')
        band_09 = ds_09.GetRasterBand(1).ReadAsArray(x, y, cols, rows).astype('float32')

        #this gives -9999 as lowest, for both band04 and band09
        #tmp1 = np.where(band_04 <= band_09, band_04, band_09)  # condition, true, false #first <= second, first, second

        #still gets -9999 from band_09, but no -9999 from band04
        tmp0 = np.where(((band_04 <= band_09) & (band_04 != -9999)), band_04, band_09)  # condition, true, false #first <= second, first, second
        #fill in -9999 from band_09(next date) with band_04(previous)
        #if both -9999, eh no worries
        #looks like it worked!
        tmp1 = np.where(tmp0==-9999,band_04,tmp0)#check where -9999, fill in with band_04(previous)

        dst_band.WriteArray(tmp1, x, y)
