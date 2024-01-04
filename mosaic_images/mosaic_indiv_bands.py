import os
from os.path import *
from osgeo import gdal
import numpy as np
import shutil

work_dir = r'E:\work\change_detect_solo'
gran = "T37RBM"
gran_dir = join(work_dir, gran)
# don't need mosaic dir, will just use month's dir
# mosaic_dir = join(gran_dir, 'mosaic')

# go into every month dir, and extract all date_6band_masked.tif
# for now, lets just move them to the month dir
for month in os.listdir(gran_dir):
    if len(month) == 6 and month.startswith('2'):
        month_dir = join(gran_dir, month)
        for date in os.listdir(month_dir):
            date_dir = join(month_dir, date)
            if isdir(date_dir):
                masked_name = f'{gran}_{date}_6band_masked.tif'
                masked_path = join(date_dir, masked_name)
                if not exists(join(month_dir, masked_name)):
                    if exists(masked_path):
                        print(f'{masked_path} to {month_dir}')
                        shutil.copy(masked_path, join(month_dir,masked_name))  # could change it to move later, but rerunning will be annoying

for month in os.listdir(gran_dir):
    mosaic_lst = []
    if len(month) == 6 and month.startswith('2'):
        month_dir = join(gran_dir, month)
        for date in os.listdir(month_dir):
            # date_dir = join(month_dir,date)
            if date.endswith('6band_masked.tif'):
                # print(date)
                mosaic_lst.append(join(month_dir, date))
        print(mosaic_lst)
        if len(mosaic_lst) == 1:  # if only one scene in month
            if not exists(join(month_dir, f'{gran}_{month}_mosaic.tif')):
                shutil.copy(mosaic_lst[0], join(month_dir, f'{gran}_{month}_mosaic.tif'))
        elif len(mosaic_lst) > 1:  # more than 1 scene
            # need to load every single raster in...
            # also all 6 bands...
            # take min, or median, of all rasters, while ignoring -9999

            ds = gdal.Open(mosaic_lst[0])
            srs_prj = ds.GetProjection()
            geoTransform = ds.GetGeoTransform()
            xsize = ds.RasterXSize
            ysize = ds.RasterYSize
            num_bands = ds.RasterCount
            ds = None

            for k in range(num_bands):
                out_k = k+1
                out_name = f'{gran}_{month}_mosaic{out_k}.tif'
                out_path = join(month_dir, out_name)

                if not exists(out_path):
                    print(f'working on mosaic {out_name}')

                    drv = gdal.GetDriverByName("GTiff")
                    dst_ds = drv.Create(out_path, xsize, ysize, 1, gdal.GDT_Int16)
                    dst_ds.SetGeoTransform(geoTransform)
                    dst_ds.SetProjection(srs_prj)
                    dst_band = dst_ds.GetRasterBand(1)
                    ds = None

                    block_xsize = 1024
                    block_ysize = 1024
                    minx = geoTransform[0]
                    miny = geoTransform[3]
                    step_x = geoTransform[1]
                    step_y = geoTransform[5]
                    count_x = 0
                    count_y = 0

                    b1_lst = []
                    for i in range(len(mosaic_lst)):
                        #print(mosaic_lst[i])
                        ds = gdal.Open(mosaic_lst[i])
                        band = ds.GetRasterBand(out_k).ReadAsArray().astype('float32')
                        band_nan = np.where(band == -9999, np.nan, band)
                        b1_lst.append(band_nan)

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
                            # mask_arr = mask_ds.GetRasterBand(1).ReadAsArray(x, y, cols, rows)
                            # got to slice up b1_lst before np.dstack
                            lst_2 = []
                            x_end = cols + x  # + 1
                            y_end = rows + y  # + 1
                            x_end = int(x_end)
                            y_end = int(y_end)
                            print(f'x {x}:{x_end}  y {y}:{y_end}')

                            for j in range(len(b1_lst)):
                                slicer = b1_lst[j][y:y_end, x:x_end]
                                # print(slicer.shape)
                                lst_2.append(slicer)

                            b1_arr = np.dstack(lst_2)
                            # print(b1_arr.shape)
                            b1_median = np.nanmedian(b1_arr, axis=2)
                            #print(f'median shape {b1_median.shape}')

                            dst_band.WriteArray(b1_median, x, y)
