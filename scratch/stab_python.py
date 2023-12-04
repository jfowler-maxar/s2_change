#Run in texveg2 env
import sys
import glob
import os
from os.path import *
from osgeo import gdal
import numpy as np
from llc import jit_filter_function

import rasterio as rio
import matplotlib.pyplot as plt

from scipy import ndimage, misc, io

@jit_filter_function
def fstd(values):
    result = np.nan
    result = np.nanstd(values)
    return result

@jit_filter_function
def fmin(values):
    result = np.nanmin(values)
    return result

@jit_filter_function
def fsum(values):
    result = np.nansum(values)
    return result

@jit_filter_function
def fmax(values):
    result = np.nanmax(values)
    return result


local_dir = r'E:\work\rpmi\cam_tests'

tile = r'T45TXH' #should be the only line that i have to change
tile_dir = join(local_dir,tile)

masked = r'masked_v01'
masked_dir = join(tile_dir,masked)
stab = r'stab_v01'
stab_dir = join(tile_dir,stab)
if not os.path.exists(stab_dir):
    os.makedirs(stab_dir, exist_ok=True)

n6=np.array([[-1, 0, 1],[-2, 0, 2],[-1, 0, 1]])

for tifs in os.listdir(masked_dir):
    if tifs.endswith(".tif"):
        in_ds = join(masked_dir,tifs)
        print(tifs)
        img_file = gdal.Open(in_ds )
        srs_prj = img_file.GetProjection()
        geoTransform = img_file.GetGeoTransform()
        x = img_file.RasterXSize
        y = img_file.RasterYSize
        b1 = img_file.GetRasterBand(1).ReadAsArray().astype('float32')
        b2 = img_file.GetRasterBand(2).ReadAsArray().astype('float32')
        b3 = img_file.GetRasterBand(3).ReadAsArray().astype('float32')
        b4 = img_file.GetRasterBand(4).ReadAsArray().astype('float32')
        b5 = img_file.GetRasterBand(5).ReadAsArray().astype('float32')
        b6 = img_file.GetRasterBand(6).ReadAsArray().astype('float32')
        img_file = None
        print('Bands read as array!')
        n60_calc =(b2-b4+0.0001)/(b2+b4+0.0001)
        n60_mem = np.where(b1>0,n60_calc,0)
        n62_mem = np.where(n60_mem>0.3,1,0)
        n60_calc = None
        n60_mem = None

        n76_temp = ndimage.generic_filter(n62_mem, fmax, footprint=np.ones((7, 7))) #7x7 matrix
        n62_mem = None
        n45_calc =(b4-b3+0.0001)/(b4+b3+0.0001)
        n45_temp = np.where(b1>0,n45_calc,0)
        n45_calc = None
        n74_temp1 = np.where(n76_temp == 0,b1,0)
        n76_temp = None
        n74_temp = np.where(n45_temp<0.4,n74_temp1,0)

        n74_temp1 = None
        n23_mem = ndimage.generic_filter(n74_temp, fstd, footprint=n6) #sobel matrixn14

        n25_mem = ndimage.generic_filter(n23_mem, fsum, footprint=np.ones((7, 7))) #7x7 matrix
        n23_mem = None
        n42_mem = ndimage.generic_filter(n25_mem, fmin, footprint=n6) #sobel matrix
        n25_mem = None
        #n91_mem = n74_temp*n42_mem/(1000000*n45_temp)
        n91_mem = n74_temp*n42_mem/(10000000*n45_temp)

        n74_temp = None
        n42_mem = None
        n45_temp = None
        n14_temp1 = np.where(n91_mem<0,0,n91_mem)
        n91_mem = None
        n14_temp2 = np.where(n14_temp1>100,100,n14_temp1)
        n14_temp = np.where(n14_temp2>=0,n14_temp2,0)
        n14_temp2 = None

        print("creating n14_temp, stab")
        out_name = tifs[:-18] + 'stab_v01.tif'
        output = join(stab_dir, out_name)

        drv = gdal.GetDriverByName("GTiff")
        dst_ds = drv.Create(output,
                            x,
                            y,
                            1,
                            gdal.GDT_Float32
                            )
        dst_ds.SetGeoTransform(geoTransform)
        dst_ds.SetProjection(srs_prj)
        dst_band = dst_ds.GetRasterBand(1)
        dst_band.WriteArray(n14_temp)
        dst_ds = None

        n120_mem = np.where(n14_temp>20,1,0)
        n122_mem = ndimage.generic_filter(n120_mem, fmax, footprint=np.ones((3, 3))) #9x9matrix
        n120_mem = None
        print('About to get to create the last mask!')
        #n124_t18suj_20200121t155551_impervious_surface = EITHER 1 IF ( $n122_memory > 0 AND $n14_temp > 10) OR 0 OTHERWISE ;
        n124 = np.where(n122_mem>0,1,0)
        n122_mem = None
        n14_temp = None

        out_name = tifs[:-18]+'stab_mask_v01.tif'
        output = join(stab_dir,out_name)

        print('creating stab_mask')
        drv = gdal.GetDriverByName("GTiff")
        dst_ds = drv.Create(output,
                            x,
                            y,
                            1,
                            gdal.GDT_Byte
                            )
        dst_ds.SetGeoTransform(geoTransform)
        dst_ds.SetProjection(srs_prj)
        dst_band = dst_ds.GetRasterBand(1)
        dst_band.WriteArray(n124)
        dst_ds = None
        n124 = None
#attempt to add n6_Custom_Float
#n6=np.array([[-1, 0, 1],[-2, 0, 2],[-1, 0, 1]])
#n6_sobel = ndimage.generic_filter(arr_pan, fstd, footprint=n6))
#n7_matrix = ndimage.generic_filter(arr_pan, fstd, footprint=np.ones((7, 7))) #7x7 matrix
#n130_matrix = ndimage.generic_filter(arr_pan, fstd, footprint=np.ones((9, 9))) #9x9matrix

