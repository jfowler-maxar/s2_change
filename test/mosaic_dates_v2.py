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

yyyy_mm_dict = {'yr_mm': [], 'tif': []}
for date in os.listdir(gran_dir):
    if len(date) == 8 and date.startswith('2'):
        date_dir = join(gran_dir, date)
        gran_date = gran + "_" + date
        yyyy_mm_dict['yr_mm'].append(date)
        masked = gran_date + '_6band_masked.tif'
        yyyy_mm_dict['tif'].append(join(date_dir, masked))

yr_mm = dict(sorted(yyyy_mm_dict.items()))  # just doing this just in case
# print(yr_mm['tif'])

month = []
for i in range(len(yr_mm['yr_mm'])):
    if i != 0:
        if yr_mm['yr_mm'][i][0:6] == yr_mm['yr_mm'][i - 1][0:6]:
            month.append(yr_mm['tif'][i])
            month.append(yr_mm['tif'][i - 1])
            # print(yr_mm['tif'][i-1])
            # print(yr_mm['tif'][i])

month1 = list(set(month))
for i in range(len(month1)):
    date = month1[i].split('\\')[4]

    # first image in month, don't need to make a tmp file for
    if i == 0:
        print(f'first scene: {month1[i]}')
    # second scene will take first image and month1[i] and make first tmp, then after that, will take all tmps

    elif i == 1:
        out_name1 = gran + f'_tmp{i}.tif'
        out_path1 = join(mosaic_dir, out_name1)
        print(out_name1)

        ds_0 = gdal.Open(month1[i - 1])  # open first scene of month
        ds = gdal.Open(month1[i])
        srs_prj = ds.GetProjection()
        geoTransform = ds.GetGeoTransform()
        xsize = ds.RasterXSize
        ysize = ds.RasterYSize
        num_bands = ds.RasterCount

        drv = gdal.GetDriverByName("GTiff")
        dst_ds = drv.Create(out_path1,
                            xsize,
                            ysize,
                            6,
                            gdal.GDT_Int16,
                            )
        dst_ds.SetGeoTransform(geoTransform)
        dst_ds.SetProjection(srs_prj)
        # dst_band = dst_ds.GetRasterBand(1)
        # dst_band.SetNoDataValue(-32768)

        # get every band of 1-6
        for j in range(1, num_bands + 1):
            band = ds.GetRasterBand(j).ReadAsArray().astype(
                'float32')  # first load up of "current"
            band_0 = ds_0.GetRasterBand(j).ReadAsArray().astype(
                'float32')  # load up previous date
            tmp0 = np.where(((band_0 <= band) & (band_0 != -9999)), band_0,
                            band)  # where previous is lower than current and not -9999
            # true = previous, false = "current"
            tmp1 = np.where(tmp0 == -9999, band_0, tmp0)  # fill in -9999 from "current" with prevous
            # if both -9999, no bid deal
            dst_band = dst_ds.GetRasterBand(j)  # output to raster band number j
            dst_band.WriteArray(tmp1)
        ds_0 = None
        ds = None

    elif i > 1 :
        out_name1 = gran + f'_tmp{i-1}.tif'
        out_path1 = join(mosaic_dir, out_name1)

        out_name2 = gran + f'_tmp{i}.tif'
        out_path2 = join(mosaic_dir, out_name2)
        print(out_name2)

        ds_0 = gdal.Open(out_path1)  # open mosaic tmp made prior
        ds = gdal.Open(month1[i])
        srs_prj = ds.GetProjection()
        geoTransform = ds.GetGeoTransform()
        xsize = ds.RasterXSize
        ysize = ds.RasterYSize
        num_bands = ds.RasterCount

        drv = gdal.GetDriverByName("GTiff")
        dst_ds = drv.Create(out_path2,
                            xsize,
                            ysize,
                            6,
                            gdal.GDT_Int16,
                            )
        dst_ds.SetGeoTransform(geoTransform)
        dst_ds.SetProjection(srs_prj)
        # dst_band = dst_ds.GetRasterBand(1)
        # dst_band.SetNoDataValue(-32768)

        # get every band of 1-6
        for j in range(1, num_bands + 1):
            band = ds.GetRasterBand(j).ReadAsArray().astype('float32')  # first load up of "current"
            band_0 = ds_0.GetRasterBand(j).ReadAsArray().astype('float32')  # load up previous date
            tmp0 = np.where(((band_0 <= band) & (band_0 != -9999)), band_0,
                            band)  # where previous is lower than current and not -9999
            # true = previous, false = "current"
            tmp1 = np.where(tmp0 == -9999, band_0, tmp0)  # fill in -9999 from "current" with prevous
            # if both -9999, no bid deal
            dst_band = dst_ds.GetRasterBand(j)  # output to raster band number j
            dst_band.WriteArray(tmp1)
        ds_0 = None
        ds = None
