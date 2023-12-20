import os
from os.path import *
from osgeo import gdal
import numpy as np
import time

work_dir = r"E:\work\change_detect_solo"
gran = "T37RBM"
gran_dir = join(work_dir, gran)
time_series_dir = join(gran_dir, 'time_series')
temporal_slope_dir = join(gran_dir, 'temp_slope')
if not exists(temporal_slope_dir):
    os.mkdir(temporal_slope_dir)

start_time = time.time()
###Set up y variable for linear regression
for stack in os.listdir(time_series_dir):
    if join(time_series_dir,stack).endswith('stack.tif'):
        bx_stack = join(time_series_dir,stack)
        outname = stack[:-4] + "tempslope.tif"
        output_path = join(temporal_slope_dir, outname)
        if not exists(output_path):
            ds = gdal.Open(bx_stack)
            srs_prj = ds.GetProjection()
            geoTransform = ds.GetGeoTransform()
            xsize = ds.RasterXSize
            ysize = ds.RasterYSize
            num_bands = ds.RasterCount

            #setup x axis(time)
            xi = np.arange(1, num_bands + 1)
            xi_mean = np.mean(xi)
            xi_x = xi - xi_mean  # "time" each input date
            xi_x2 = xi_x * xi_x  # squared
            sum_x2 = np.sum(xi_x2)

            # setup output
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
            dst_band.SetNoDataValue(-9999)

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
                #print(f'block x: {x}')
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
                    #print(f'Going through stack \n{bx_stack}')
                    array_layers = []
                    for i in range(1, num_bands+1):
                        #print("layer number: {}".format(i))
                        band = ds.GetRasterBand(i).ReadAsArray(x,y,cols,rows).astype('float32')
                        arr = np.where(band == -9999, np.nan, band)
                        array_layers.append(arr)
                    #get avg for all arrays
                    arr_mean = np.nanmean(array_layers, axis=0)  # get mean array of all layers
                    #y = a + bx
                    for k in range(len(array_layers)):
                        array_layers[k][np.isnan(array_layers[k])] = arr_mean[np.isnan(array_layers[k])]
                        yi_y = array_layers[k] - arr_mean
                        x_y = yi_y * xi_x[k]  # (xi-x)*(yi-y)
                        # need sum...
                        if k == 0:
                            sum_xy = x_y
                        else:
                            sum_xy = x_y + sum_xy
                    # y=a+bx
                    outSlope = sum_xy / sum_x2  # slope
                    # a = arr_mean - b*(num_bands) #intercept
                    dst_band.WriteArray(outSlope, x, y)

    print(f'done with {bx_stack}\n{output_path} should be done')
    print("--- %s seconds ---" % (time.time() - start_time))
    if join(time_series_dir, stack).endswith('stack.vrt'):
        bx_stack = join(time_series_dir, stack)
        outname = stack[:-4] + "tempslope.tif"
        output_path = join(temporal_slope_dir, outname)
        if not exists(output_path):
            ds = gdal.Open(bx_stack)
            srs_prj = ds.GetProjection()
            geoTransform = ds.GetGeoTransform()
            xsize = ds.RasterXSize
            ysize = ds.RasterYSize
            num_bands = ds.RasterCount

            # setup x axis(time)
            xi = np.arange(1, num_bands + 1)
            xi_mean = np.mean(xi)
            xi_x = xi - xi_mean  # "time" each input date
            xi_x2 = xi_x * xi_x  # squared
            sum_x2 = np.sum(xi_x2)

            # setup output
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
            dst_band.SetNoDataValue(-9999)

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
                print(f'block x: {x}')
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
                    print(f'block y: {y}')
                    if y + block_ysize < ysize:
                        rows = block_ysize
                        y_off = miny + (count_y * step_y)
                        count_y = count_y + block_ysize
                    else:
                        rows = ysize - y
                        y_off = miny + (count_y * step_y)
                        count_y = count_y + y

                    # this is where calculations/data maniuplations happen
                    #print(f'Going through stack \n{bx_stack}')
                    array_layers = []
                    for i in range(1, num_bands + 1):
                        # print("layer number: {}".format(i))
                        band = ds.GetRasterBand(i).ReadAsArray(x, y, cols, rows).astype('float32')
                        arr = np.where(band == -9999, np.nan, band)
                        array_layers.append(arr)
                    # get avg for all arrays
                    arr_mean = np.nanmean(array_layers, axis=0)  # get mean array of all layers
                    # y = a + bx
                    for k in range(len(array_layers)):
                        array_layers[k][np.isnan(array_layers[k])] = arr_mean[np.isnan(array_layers[k])]
                        yi_y = array_layers[k] - arr_mean
                        x_y = yi_y * xi_x[k]  # (xi-x)*(yi-y)
                        # need sum...
                        if k == 0:
                            sum_xy = x_y
                        else:
                            sum_xy = x_y + sum_xy
                    # y=a+bx
                    outSlope = sum_xy / sum_x2  # slope
                    # a = arr_mean - b*(num_bands) #intercept
                    dst_band.WriteArray(outSlope, x, y)