import os
from os.path import *
from osgeo import gdal

# import numpy as np

# test using block size to output chips
# for now, just output 1 band chips, figure out how to turn into a function later to use for scientific funtions

local_dir = r'E:\work\change_detect_solo'
tile = 'T18SUJ'
tile_dir = join(local_dir, tile)
date = '20221221'
date_dir = join(tile_dir, date)

input_file = join(date_dir, tile + '_' + date + '_6band.vrt')
# input_file = r"E:\work\change_detect_solo\T18SUJ\20221221\MSIL2A\T18SUJ_20221221T155659_B02_10m.jp2"
# only vrt has block sizes 128x128, all others have blocks 10980x1... gonnna have to go back and fix that lol
if not exists(input_file):
    print('oops')
    print('{} does not exist'.format(input_file))
    exit(1)

in_ds = gdal.Open(input_file)
srs_prj = in_ds.GetProjection()
geoTransform = in_ds.GetGeoTransform()
band_1 = in_ds.GetRasterBand(1)
xsize = band_1.XSize
ysize = band_1.YSize
block_xsize, block_ysize = band_1.GetBlockSize()
nodata = band_1.GetNoDataValue()

print(geoTransform)

scratch_dir = join(date_dir, 'scatch')
if not exists(scratch_dir):
    os.mkdir(scratch_dir)

print('creating chips!')
print('for now, just band 1 chips')
###
#creating one complete image, doing it 10x blocks at a time
drv = gdal.GetDriverByName("GTiff")
out_ds = drv.Create(r'E:\work\change_detect_solo\T18SUJ\20221221\scatch\test.tif',
                    xsize,
                    ysize,
                    1,
                    gdal.GDT_Int16,
                    options=["TILED=YES","BLOCKXSIZE={}".format(block_xsize),"BLOCKYSIZE={}".format(block_ysize)]
                    )
out_ds.SetGeoTransform(geoTransform)
out_ds.SetProjection(srs_prj)
out_band = out_ds.GetRasterBand(1)
#created file, will be populated by arrays
###
block_xsize = block_xsize * 10
block_ysize = block_ysize * 10
minx = geoTransform[0]
miny = geoTransform[3]
step_x = geoTransform[1]
step_y = geoTransform[5]
count_x = 0
count_y = 0

for x in range(0, xsize, block_xsize):
    print(x)
    if x + block_xsize < xsize:
        cols = block_xsize
        x_off = minx + (count_x*step_x)
        count_x = count_x + block_xsize
    else:
        cols = xsize - x
        x_off = minx + (count_x*step_x)
        count_x = count_x + x
    count_y = 0
    for y in range(0, ysize, block_ysize):
        if y + block_ysize < ysize:
            rows = block_ysize
            y_off = miny + (count_y*step_y)
            count_y = count_y + block_ysize
        else:
            rows = ysize - y
            y_off = miny + (count_y*step_y)
            count_y = count_y + y
        # this is where calculations/data maniuplations happen
        arr_1 = band_1.ReadAsArray(x, y, cols, rows)
        #Below is where calculations would go


        out_band.WriteArray(arr_1, x, y)  # writing to test.tif

        #below is if want to output all the chips, otherwise ignore
        output_name = tile + '_' + date + '_x' + str(x) + '_y' + str(y) + '.tif'
        output = join(scratch_dir, output_name)
        if not exists(output):
            drv = gdal.GetDriverByName("GTiff")
            dst_ds = drv.Create(output,
                                cols,
                                rows,
                                1,
                                gdal.GDT_Int16
                                )
            geoTransform_lst = list(geoTransform)
            geoTransform_lst[0] = x_off
            geoTransform_lst[3] = y_off
            geoTransform = tuple(geoTransform_lst)
            dst_ds.SetGeoTransform(geoTransform)
            dst_ds.SetProjection(srs_prj)
            dst_band = dst_ds.GetRasterBand(1)
            dst_band.WriteArray(arr_1)
            dst_ds = None

out_ds = None