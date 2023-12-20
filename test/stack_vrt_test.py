import os
from os.path import *
from osgeo import gdal
import numpy as np
import numpy.ma as ma
from normalize_dif_test import indicies

work_dir = r"E:\work\change_detect_solo"
gran = "T18SUJ"
gran_dir = join(work_dir, gran)
index = indicies(gran)

# create 6band_stack.vrt
for date in os.listdir(gran_dir):
    if len(date) == 8 and date.startswith('2'):
        # print(join(gran_dir,date))
        l2a_dir = join(gran_dir, date, 'MSIL2A')
        jp2_list = []
        gran_date = gran + "_" + date
        dst_6band = join(gran_dir, date, gran_date + '_6band.vrt')
        if exists(l2a_dir) == False:
            print('MSIL2A dir does not exist! Cant do anything')
            exit(2)
        if exists(l2a_dir):
            print('running 6band stack on L2A')
            if not exists(dst_6band):
                for jp2 in os.listdir(l2a_dir):
                    if jp2.endswith('.jp2'):
                        if jp2.endswith('B02_10m.jp2'):
                            jp2_list.append(join(l2a_dir, jp2))
                        elif jp2.endswith('B03_10m.jp2'):
                            jp2_list.append(join(l2a_dir, jp2))
                        elif jp2.endswith('B04_10m.jp2'):
                            jp2_list.append(join(l2a_dir, jp2))
                        elif jp2.endswith('B08_10m.jp2'):
                            jp2_list.append(join(l2a_dir, jp2))
                        elif jp2.endswith('B11_20m.jp2'):
                            jp2_list.append(join(l2a_dir, jp2))
                        elif jp2.endswith('B12_20m.jp2'):
                            jp2_list.append(join(l2a_dir, jp2))
                        elif jp2.endswith('SCL_20m.jp2'):  # grab scl for cloud mask
                            scl = join(l2a_dir, jp2)
                jp2_list.sort()
                # print(jp2_list)
                print('Creating ' + dst_6band)
                gdal.BuildVRT(dst_6band, jp2_list, separate='separate', resolution='highest')
            if not exists(dst_6band):
                print('welp something went wrong')
                exit(4)

# run through again cause too messy
# gonna attempt to grab b10
# will point to scl and newly create 6band.vrt
for date in os.listdir(gran_dir):
    if len(date) == 8 and date.startswith('2'):
        l1c_dir = join(gran_dir, date, 'MSIL1C')
        l2a_dir = join(gran_dir, date, 'MSIL2A')
        gran_date = gran + "_" + date
        dst_6band = join(gran_dir, date, gran_date + '_6band.vrt')
        print('Starting masking for {}'.format(dst_6band))
        if not exists(dst_6band):
            print('SHITTTT')
            print('{} not found'.format(dst_6band))
            exit(11)
        if not exists(l1c_dir):
            print('MSIL1C dir does not exist!')
            print('no b10 for cloud masking oh well')
        elif exists(l1c_dir):
            print('MSIL1C exits, grabbing b10')
            for jp2 in os.listdir(l1c_dir):
                if jp2.endswith('.jp2'):
                    if jp2.endswith('B10.jp2'):
                        b10_path = join(l1c_dir, jp2)

        for jp2 in os.listdir(l2a_dir):
            if jp2.endswith('SCL_20m.jp2'):
                scl = join(l2a_dir, jp2)  # for cloud masks

        print('Open scl')
        scl_file = gdal.Open(scl)
        scl_class = scl_file.GetRasterBand(1)
        scl_x = scl_class.XSize * 2
        scl_y = scl_class.YSize * 2
        scl_class = scl_class.ReadAsArray(buf_xsize=scl_x, buf_ysize=scl_y).astype('uint16')
        # scl classes for the mask: Nodata(0),Saturated(1),cloudshadows(3),cloud med (8), cloud high (9)
        scl_file = None
        print('Open vrt')
        vrt_file = gdal.Open(dst_6band)
        srs_prj = vrt_file.GetProjection()
        geoTransform = vrt_file.GetGeoTransform()
        xsize = vrt_file.RasterXSize
        ysize = vrt_file.RasterYSize
        print('vrt get raster bands!')
        vrt_b1 = vrt_file.GetRasterBand(1).ReadAsArray().astype('uint16')
        vrt_b2 = vrt_file.GetRasterBand(2).ReadAsArray().astype('uint16')
        vrt_b3 = vrt_file.GetRasterBand(3).ReadAsArray().astype('uint16')
        vrt_b4 = vrt_file.GetRasterBand(4).ReadAsArray().astype('uint16')
        vrt_b5 = vrt_file.GetRasterBand(5).ReadAsArray().astype('uint16')
        vrt_b6 = vrt_file.GetRasterBand(6).ReadAsArray().astype('uint16')
        vrt_file = None

        print('SCL class simplifiacation')

        masked_tif = join(gran_dir, date, gran_date + '_6band_masked.tif')
        print('creating {}'.format(masked_tif))

        drv = gdal.GetDriverByName("GTiff")
        dst_ds = drv.Create(masked_tif,
                            xsize,
                            ysize,
                            6,
                            gdal.GDT_Int16,
                            options=["TILED=YES", "BLOCKXSIZE=256",
                                     "BLOCKYSIZE=256"]
                            )
        dst_ds.SetGeoTransform(geoTransform)
        dst_ds.SetProjection(srs_prj)
        out_band1 = dst_ds.GetRasterBand(1)
        out_band2 = dst_ds.GetRasterBand(2)
        out_band3 = dst_ds.GetRasterBand(3)
        out_band4 = dst_ds.GetRasterBand(4)
        out_band5 = dst_ds.GetRasterBand(5)
        out_band6 = dst_ds.GetRasterBand(6)

        chip_x, chip_y, minx, miny, step_x, step_y = index.set_chip(dst_6band, 256, 256)
        count_x = 0
        count_y = 0

        for x in range(0, xsize, chip_x):
            print('x is on: '+x)
            if x + chip_x < xsize:
                cols = chip_x
                x_off = minx + (count_x * step_x)
                count_x = count_x + chip_x
            else:
                cols = xsize - x
                x_off = minx + (count_x * step_x)
                count_x = count_x + x
            count_y = 0
            for y in range(0, ysize, chip_y):
                print('y in is on: '+y)
                if y + chip_y < ysize:
                    rows = chip_y
                    y_off = miny + (count_y * step_y)
                    count_y = count_y + chip_y
                else:
                    rows = ysize - y
                    y_off = miny + (count_y * step_y)
                    count_y = count_y + y

                # mask = np.where(scl_class==1 or scl_class==3 or scl_class==8 or scl_clas==9,scl_class,0)
                mask1 = ma.masked_where(scl_class == 1, scl_class) #DOUBLE CHECK TO MAKE SURE THIS BLOCK MAKES SENSE
                mask2 = ma.masked_where(mask1 == 3, mask1)
                mask3 = ma.masked_where(mask2 == 8, mask2)
                mask4 = ma.masked_where(mask3 == 9, mask3)
                mask5 = ma.masked_where(mask4 != 0, mask4)
                # set 0 to -9999, because I want nodata to be -9999 (if it's nodata=0 later things getting annoying)
                mask6 = ma.masked_where(mask5 == 0, mask5)

                clip1 = ma.masked_where(mask6 == 1, vrt_b1)
                clip2 = ma.masked_where(mask6 == 1, vrt_b2)
                clip3 = ma.masked_where(mask6 == 1, vrt_b3)
                clip4 = ma.masked_where(mask6 == 1, vrt_b4)
                clip5 = ma.masked_where(mask6 == 1, vrt_b5)
                clip6 = ma.masked_where(mask6 == 1, vrt_b6)

                out_band1 = dst_ds.GetRasterBand(1)
                out_band1.WriteArray(clip1)
                out_band1.SetNoDataValue(-9999)

                dst_band2 = dst_ds.GetRasterBand(2)
                out_band2.WriteArray(clip2)
                out_band2.SetNoDataValue(-9999)

                out_band3 = dst_ds.GetRasterBand(3)
                out_band3.WriteArray(clip3)
                out_band3.SetNoDataValue(-9999)

                out_band4 = dst_ds.GetRasterBand(4)
                out_band4.WriteArray(clip4)
                out_band4.SetNoDataValue(-9999)

                out_band5 = dst_ds.GetRasterBand(5)
                out_band5.WriteArray(clip5)
                dst_band5.SetNoDataValue(-9999)

                out_band6 = dst_ds.GetRasterBand(6)
                out_band6.WriteArray(clip6)
                out_band6.SetNoDataValue(-9999)

        clip1, clip2, clip3, clip4, clip5, clip6 = None
        scl_class, mask1, mask2, mask3, mask4, mask5 = None, None, None, None, None, None
        vrt_b1, vrt_b2, vrt_b3, vrt_b4, vrt_b5, vrt_b6 = None, None, None, None, None, None
        dst_ds = None
        # now i can use 6 band stack to create ndvi, ndbi,msavi, whatever i want
