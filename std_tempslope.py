import os
from os.path import *
from osgeo import gdal
import numpy as np

work_dir = r'D:\s2_change\tiles'
gran = "T49QDD"
gran_dir = join(work_dir, gran)
time_series_dir = join(gran_dir, 'time_series')
temporal_slope_dir = join(gran_dir, 'temp_slope')
chang_dir = join(gran_dir, 'change')
if not exists(chang_dir):
    os.mkdir(chang_dir)

# create water mask to avoid water throwing off std values
watername = 'water_mask.tif'
water_out = join(chang_dir, watername)
if not exists(water_out):
    print('creating water mask')
    ndwi_series = join(time_series_dir, gran + '_ndwi_stack.vrt')
    if not exists(ndwi_series):
        print(f'{ndwi_series} DNE')
        exit(1)
    ds = gdal.Open(ndwi_series)
    srs_prj = ds.GetProjection()
    geoTransform = ds.GetGeoTransform()
    xsize = ds.RasterXSize
    ysize = ds.RasterYSize
    num_bands = ds.RasterCount

    drv = gdal.GetDriverByName("GTiff")
    dst_ds = drv.Create(water_out,
                        xsize,
                        ysize,
                        1,
                        gdal.GDT_Byte,
                        )
    dst_ds.SetGeoTransform(geoTransform)
    dst_ds.SetProjection(srs_prj)
    dst_band = dst_ds.GetRasterBand(1)
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
            array_layers = []
            for i in range(1, num_bands + 1):
                # print("layer number: {}".format(i))
                band = ds.GetRasterBand(i).ReadAsArray(x, y, cols, rows).astype('float32')
                arr = np.where(band == -100, np.nan, band)
                array_layers.append(arr)
            water_arr = np.nanmean(array_layers, axis=0)
            water_mask = np.where(water_arr >= 10, 0, 1)  # np.where(condition,True output, False output)
            dst_band.WriteArray(water_mask, x, y)

ds = None
dst_ds = None

if not exists(water_out):
    print(f'creating {water_out} failed')
    exit(2)

mask_ds = gdal.Open(water_out)

for slope in os.listdir(temporal_slope_dir):
    if join(temporal_slope_dir, slope).endswith('tempslope.tif'):
        bx_stack = join(temporal_slope_dir, slope)
        outname = slope[:-4] + "_std.tif"
        output_path = join(chang_dir, outname)
        if not exists(output_path):
            ds = gdal.Open(bx_stack)
            srs_prj = ds.GetProjection()
            geoTransform = ds.GetGeoTransform()
            xsize = ds.RasterXSize
            ysize = ds.RasterYSize
            num_bands = ds.RasterCount

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
                    arr = ds.GetRasterBand(1).ReadAsArray(x, y, cols, rows).astype('float32')
                    # setup water mask
                    mask_arr = mask_ds.GetRasterBand(1).ReadAsArray(x, y, cols, rows)
                    masked_arr = np.where(mask_arr == 0, np.nan, arr)
                    arr_std = np.nanstd(masked_arr)  # this gives one std value for entire raster
                    # now will compare this arr_std to all other pixels to see how many std's off it is
                    out_arr = masked_arr / arr_std

                    dst_band.WriteArray(out_arr, x, y)
