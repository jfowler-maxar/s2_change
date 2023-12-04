import os
from os.path import *
from osgeo import gdal
import numpy as np

local_dir = r'E:\work\rpmi\cam_tests'

tile = r'T37REK' #should be the only line that i have to change
tile_dir = join(local_dir,tile)

masked = r'masked'
masked_dir = join(tile_dir,masked)
ndvi = r'ndvi'

ndvi_dir = join(tile_dir,ndvi)
if not os.path.exists(ndvi_dir):
    os.makedirs(ndvi_dir, exist_ok=True)
#create ndvi files
for tifs in os.listdir(masked_dir):
    if tifs.endswith(".tif"):
        in_ds = join(masked_dir,tifs)
        print(tifs)
        img_file = gdal.Open(in_ds )
        srs_prj = img_file.GetProjection()
        geoTransform = img_file.GetGeoTransform()
        x = img_file.RasterXSize
        y = img_file.RasterYSize
        #blue = img_file.GetRasterBand(1).ReadAsArray().astype('float32')
        #green = img_file.GetRasterBand(2).ReadAsArray().astype('float32')
        b4 = img_file.GetRasterBand(4).ReadAsArray().astype('float32')
        b3 = img_file.GetRasterBand(3).ReadAsArray().astype('float32')
        img_file = None

        #grayscale formula
        #calc = red * 0.2989 + green * 0.5870 + blue * 0.1140
        #gdal_calc.py -R input.tif --R_band=1 -G input.tif --G_band=2 -B input.tif --B_band=3 --outfile=result.tif --calc="R*0.2989+G*0.5870+B*0.1140"
        yr = tifs.split('_')[3]
        if int(yr) >= 20220125: #post jan 25, 2022 scenes subtract 1000
            calc = ((b4-1000) - (b3-1000) + .0001) / ((b4-1000)  + (b3-1000)+.0001) * 100
        else:
            calc = (b4-b3+.0001)/(b4+b3)*100

        clamp_neg_100 = np.where(
            calc >= -100,calc,-100)
        clamp_over_100 = np.where(
            clamp_neg_100 <= 100,clamp_neg_100,100)

        out_name = tifs[:-4]+'_ndvi.tif'
        output = join(ndvi_dir,out_name)

        drv = gdal.GetDriverByName("GTiff")
        dst_ds = drv.Create(output,
                            x,
                            y,
                            1,
                            gdal.GDT_Int16,
                            options=["COMPRESSED=YES"])
        dst_ds.SetGeoTransform(geoTransform)
        dst_ds.SetProjection(srs_prj)
        dst_band = dst_ds.GetRasterBand(1)
        dst_band.WriteArray(clamp_over_100)

        dst_ds = None