import os
from os.path import *
from osgeo import gdal
import numpy as np


'''def do_raster_stats(array_stack,stat):
    #print('Doing dstack')
    #raster_stack = np.dstack(list_of_arrays)
    if stat=='std':
        print('calculating std raster')
        out_array = np.nanstd(array_stack, axis=2)
    elif stat=='mean':
        print('calculating mean raster')
        out_array = np.nanmean(array_stack, axis=2)
    elif stat=='median':
        print('calculating median raster')
        out_array = np.nanmedian(array_stack, axis=2)
    elif stat=='range':
        print('calculating range raster')
        max_array = np.nanmax(array_stack, axis=2)
        min_array = np.nanmin(array_stack, axis=2)
        out_array = max_array-min_array
    else:
        print('something wrong in do_raster_stats')
        exit(10)
    return(out_array)'''


def main():
    work_dir = r'D:\s2_change\tiles'
    gran = "T49QDD"
    gran_dir = join(work_dir, gran)
    time_series_dir = join(gran_dir, 'time_series')
    time_stats_dir = join(gran_dir,'time_stats')
    if exists(time_stats_dir) == False:
        os.mkdir(time_stats_dir)

    for stack in os.listdir(time_series_dir):
        if join(time_series_dir, stack).endswith('stack.tif') or join(time_series_dir, stack).endswith('stack.vrt'):
            bx_stack = join(time_series_dir, stack)

            stat = bx_stack.split('_')[-2]
            mean_raster = join(time_stats_dir, gran + "_" + stat + '_mean.tif')
            median_raster = join(time_stats_dir, gran + "_" + stat + '_median.tif')
            std_rastar = join(time_stats_dir, gran + "_" + stat + '_std.tif')
            #range_raster = join(time_stats_dir, gran + "_" + stat + '_range.tif')

            #output_path = join(temporal_slope_dir, outname)
            if not exists(mean_raster):
                ds = gdal.Open(bx_stack)
                srs_prj = ds.GetProjection()
                geoTransform = ds.GetGeoTransform()
                xsize = ds.RasterXSize
                ysize = ds.RasterYSize
                num_bands = ds.RasterCount

                # setup output
                drv = gdal.GetDriverByName("GTiff")
                dst_ds = drv.Create(mean_raster,
                                    xsize,
                                    ysize,
                                    1,
                                    gdal.GDT_Int16,
                                    )
                dst_ds.SetGeoTransform(geoTransform)
                dst_ds.SetProjection(srs_prj)
                dst_band = dst_ds.GetRasterBand(1)
                dst_band.SetNoDataValue(-32768)

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
                        # print(f'Going through stack \n{bx_stack}')
                        array_layers = []
                        for i in range(1, num_bands + 1):
                            # print("layer number: {}".format(i))
                            band = ds.GetRasterBand(i).ReadAsArray(x, y, cols, rows).astype('float32')
                            arr = np.where(band < 0, np.nan, band)
                            array_layers.append(arr)
                        # get avg for all arrays
                        #both methods work! dstack, then axis=2, orrrr no dstack and jus[t take axis=0 for the list of arrays
                        #1#raster_stack = np.dstack(array_layers)
                        #2#arr_mean = np.nanmean(raster_stack, axis=2)  # get mean array of all layers
                        arr_mean = np.nanmean(array_layers, axis=0)  # get mean array of all layers
                        dst_band.WriteArray(arr_mean, x, y)

            if not exists(median_raster):
                ds = gdal.Open(bx_stack)
                srs_prj = ds.GetProjection()
                geoTransform = ds.GetGeoTransform()
                xsize = ds.RasterXSize
                ysize = ds.RasterYSize
                num_bands = ds.RasterCount

                # setup output
                drv = gdal.GetDriverByName("GTiff")
                dst_ds = drv.Create(mean_raster,
                                    xsize,
                                    ysize,
                                    1,
                                    gdal.GDT_Int16,
                                    )
                dst_ds.SetGeoTransform(geoTransform)
                dst_ds.SetProjection(srs_prj)
                dst_band = dst_ds.GetRasterBand(1)
                dst_band.SetNoDataValue(-32768)

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
                        # print(f'Going through stack \n{bx_stack}')
                        array_layers = []
                        for i in range(1, num_bands + 1):
                            # print("layer number: {}".format(i))
                            band = ds.GetRasterBand(i).ReadAsArray(x, y, cols, rows).astype('float32')
                            arr = np.where(band < 0, np.nan, band)
                            array_layers.append(arr)
                        # get avg for all arrays
                        #both methods work! dstack, then axis=2, orrrr no dstack and jus[t take axis=0 for the list of arrays
                        #1#raster_stack = np.dstack(array_layers)
                        #2#arr_mean = np.nanmean(raster_stack, axis=2)  # get mean array of all layers
                        arr_med = np.nanmedian(array_layers, axis=0)  # get mean array of all layers
                        dst_band.WriteArray(arr_med, x, y)

            if not exists(std_rastar):
                ds = gdal.Open(bx_stack)
                srs_prj = ds.GetProjection()
                geoTransform = ds.GetGeoTransform()
                xsize = ds.RasterXSize
                ysize = ds.RasterYSize
                num_bands = ds.RasterCount

                # setup output
                drv = gdal.GetDriverByName("GTiff")
                dst_ds = drv.Create(mean_raster,
                                    xsize,
                                    ysize,
                                    1,
                                    gdal.GDT_Int16,
                                    )
                dst_ds.SetGeoTransform(geoTransform)
                dst_ds.SetProjection(srs_prj)
                dst_band = dst_ds.GetRasterBand(1)
                dst_band.SetNoDataValue(-32768)

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
                        # print(f'Going through stack \n{bx_stack}')
                        array_layers = []
                        for i in range(1, num_bands + 1):
                            # print("layer number: {}".format(i))
                            band = ds.GetRasterBand(i).ReadAsArray(x, y, cols, rows).astype('float32')
                            arr = np.where(band < 0, np.nan, band)
                            array_layers.append(arr)
                        # get avg for all arrays
                        #both methods work! dstack, then axis=2, orrrr no dstack and jus[t take axis=0 for the list of arrays
                        #1#raster_stack = np.dstack(array_layers)
                        #2#arr_mean = np.nanmean(raster_stack, axis=2)  # get mean array of all layers
                        arr_std = np.nanstd(array_layers, axis=0)  # get mean array of all layers
                        dst_band.WriteArray(arr_std, x, y)

if __name__ == "__main__":
    main()