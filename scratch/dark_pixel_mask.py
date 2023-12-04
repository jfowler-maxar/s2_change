import copy
import os
from os.path import *
from osgeo import gdal
import numpy as np

local_dir = r'C:\Users\ju007307\Documents\rpmi\cam3'

tile = r'T49QGF' #should be the only line that i have to change
tile_dir = join(local_dir,tile)
darkmask = r'darkmask'
out_dir = join(tile_dir,darkmask)
if not os.path.exists(out_dir):
    os.makedirs(out_dir, exist_ok=True)
masked = r'masked'
masked_dir = join(tile_dir,masked)
ndvi = r'ndvi'
ndvi_dir = join(tile_dir,ndvi)
grayscale = r'grayscale'
grayscale_dir = join(tile_dir,grayscale)

#create dark pixel masks
#inputs: terrain_shadow layer (cosi), ndvi, grayscale image
terrain_shadow_layer_name = r'T49QGF_S2B_20211205_terrain_shadow.img'
terrain_shadow_layer = join(tile_dir,terrain_shadow_layer_name)
gray_layer_name = r'T49QGF_S2B_p000r000_20211205_gray.tif'
gray_layer = join(grayscale_dir,gray_layer_name)
ndvi_layer_name = r'T49QGF_S2B_p000r000_20211205_ndvi.tif'
ndvi_layer = join(ndvi_dir,ndvi_layer_name)

tshadow_file = gdal.Open(terrain_shadow_layer)
gray_file = gdal.Open(gray_layer)
ndvi_file = gdal.Open(ndvi_layer)

srs_prj = tshadow_file.GetProjection()
geoTransform = tshadow_file.GetGeoTransform()

x = tshadow_file.RasterXSize
y = tshadow_file.RasterYSize
tshadow_array = tshadow_file.GetRasterBand(1).ReadAsArray(0,0,x,y).astype('float32')

x = gray_file.RasterXSize
y = gray_file.RasterYSize
gray_array = gray_file.GetRasterBand(1).ReadAsArray(0,0,x,y).astype('float32')

x = ndvi_file.RasterXSize
y = ndvi_file.RasterYSize
ndvi_array = ndvi_file.GetRasterBand(1).ReadAsArray(0,0,x,y).astype('float32')

tshadow_file = None
gray_file = None
ndvi_file = None

#imgmath_gb.exe -eq "(cosi<31 or cosi>100) or (gray<300 and gray>0) ? 1:0"
#og imgmath did NOT include ndvi thresh
#terrain shadow: cosi <31 or cosi >100
#OR statement
#grayscale and ndvi: gray<300 and ndvi < thresh(from global settings)
ts_thresh = 31
gray_thresh = 300
ndvi_thresh = 72

#terrain shadow
mask = copy.copy(tshadow_array)
mask[mask>100] = 1 #values greater than 100 are outliers/nodata types
mask[mask<ts_thresh] = 1
mask[tshadow_array>=ts_thresh] = 0
#grayscale with the ndvi values adjusted
mask2 = copy.copy(gray_array)
mask2[ndvi_array>ndvi_thresh] = 301 #sets all VEG to bright value
mask2[mask2<gray_thresh] =1 #gray that is less than 300 AND not Veg goes to mask value
#final version
mask3 = copy.copy(mask)
mask3[mask2==1] = 1 #combining terrain_shadow mask with darkness mask

out_name = terrain_shadow_layer_name[:-18]+"cosi31_gray300_ndvi.tif"
output = join(out_dir, out_name)

drv = gdal.GetDriverByName("GTiff")
dst_ds = drv.Create(output,
                    x,
                    y,
                    1,
                    gdal.GDT_Byte,
                    )
dst_ds.SetGeoTransform(geoTransform)
dst_ds.SetProjection(srs_prj)
dst_band = dst_ds.GetRasterBand(1)
dst_band.WriteArray(mask3)
dst_ds = None