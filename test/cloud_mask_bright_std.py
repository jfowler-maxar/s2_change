import os
from os.path import *
from osgeo import gdal
import numpy as np

work_dir = r"E:\work\change_detect_solo"
gran = "T20LMR"
gran_dir = join(work_dir,gran)

in_tif = r"E:\work\change_detect_solo\T20LMR\20230301\T20LMR_20230301_6band.vrt"
ds = gdal.Open(in_tif)
srs_prj = ds.GetProjection()
geoTransform = ds.GetGeoTransform()
xsize = ds.RasterXSize
ysize = ds.RasterYSize

cld_mask = r'E:\work\change_detect_solo\T20LMR\20230301\T20LMR_20230301_cloud_mask_std2.tif'
drv = gdal.GetDriverByName("GTiff")
dst_ds = drv.Create(cld_mask,
                    xsize,
                    ysize,
                    1,
                    gdal.GDT_Int16,
                    )
dst_ds.SetGeoTransform(geoTransform)
dst_ds.SetProjection(srs_prj)
dst_band = dst_ds.GetRasterBand(1)

#grab b1, blue band cause cloud should be brightest there, maybe
band = ds.GetRasterBand(1).ReadAsArray().astype('float32')
no_0s = np.where(band<=0,np.nan,band)
std_raster = np.nanstd(no_0s) #this should just be one number
avg_raster = np.nanmean(no_0s)

#now idea is pixel values that are 3std's away from the avg would be cloud
#lets just do bright only, cause could always do cloud shadow using dem/sun angles later
std_3 = std_raster*2
print(avg_raster)
print(std_raster)
print(std_3)
std_3_over_avg = avg_raster+std_3
print(std_3_over_avg)
mask = np.where(no_0s >=std_3_over_avg,0,1)#0 for mask, 1 for land

dst_band.WriteArray(mask)