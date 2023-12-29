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

month1 = list(set(month))

#get all b1's for each month
for i in range(len(month1)):
    m = month1[i].split('\\')[4][0:6]
    #print(m)
    if i == 0:
        print(month1[i].split('\\')[4])
    elif i > 0:
        print(month1[i].split('\\')[4])
        b1_lst = []
        if m == month1[i-1].split('\\')[4][0:6]:
            ds = gdal.Open(month1[i])
            srs_prj = ds.GetProjection()
            geoTransform = ds.GetGeoTransform()
            xsize = ds.RasterXSize
            ysize = ds.RasterYSize
            #num_bands = ds.RasterCount
            band = ds.GetRasterBand(1).ReadAsArray().astype('float32')
            arr = np.where(band==-9999,np.nan,band)
            b1_lst.append(arr)
            ds = None
            #print(b1_lst)
        if len(b1_lst) != 0:
            b1_stack = np.dstack(b1_lst)
            b1_median = np.nanmedian(b1_stack,axis=2)
            b1_mean = np.nanmean(b1_stack,axis=2)

            #median
            out_name = f'{gran}_{m}_med.tif'
            out_path = join(mosaic_dir, out_name)
            drv = gdal.GetDriverByName("GTiff")
            dst_ds = drv.Create(out_path,
                                xsize,
                                ysize,
                                1,
                                gdal.GDT_Int16,
                                )
            dst_ds.SetGeoTransform(geoTransform)
            dst_ds.SetProjection(srs_prj)
            dst_band = dst_ds.GetRasterBand(1)
            dst_band.WriteArray(b1_median)

            #mean
            out_name = f'{gran}_{m}_mean.tif'
            out_path = join(mosaic_dir, out_name)
            drv = gdal.GetDriverByName("GTiff")
            dst_ds = drv.Create(out_path,
                                xsize,
                                ysize,
                                1,
                                gdal.GDT_Int16,
                                )
            dst_ds.SetGeoTransform(geoTransform)
            dst_ds.SetProjection(srs_prj)
            dst_band = dst_ds.GetRasterBand(1)
            dst_band.WriteArray(b1_mean)
        if m != month1[i-1].split('\\')[4][0:6]:
            b1_lst = []