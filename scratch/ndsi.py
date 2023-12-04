import os
from os.path import *
from osgeo import gdal
import numpy as np

local_dir = r'E:\work\rpmi\cam_tests'

tile = r'T45TXH' #should be the only line that i have to change
tile_dir = join(local_dir,tile)

masked = r'masked'
masked_dir = join(tile_dir,masked)
ndsi = r'ndsi'

ndsi_dir = join(tile_dir,ndsi)
if not os.path.exists(ndsi_dir):
    os.makedirs(ndsi_dir, exist_ok=True)
#create ndsi files
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
        b2 = img_file.GetRasterBand(2).ReadAsArray().astype('float32')
        b5 = img_file.GetRasterBand(5).ReadAsArray().astype('float32')
        img_file = None

        #grayscale formula
        #gdal_calc.py -R input.tif --R_band=1 -G input.tif --G_band=2 -B input.tif --B_band=3 --outfile=result.tif --calc="R*0.2989+G*0.5870+B*0.1140"
        #calc = red*0.2989+green*0.5870+blue*0.1140
        yr = tifs.split('_')[3]
        if int(yr) >= 20220125: #post jan 25, 2022 scenes subtract 1000
            calc = ((b2-1000) - (b5-1000) + .0001) / ((b2-1000)  + (b5-1000)+.0001) * 100
        else:
            calc = (b2-b5+.0001)/(b2+b5)*100

        clamp_neg_100 = np.where(
            calc >= -100,calc,-100)
        clamp_over_100 = np.where(
            clamp_neg_100 <= 100,clamp_neg_100,100)

        out_name = tifs[:-4]+'_ndsi.tif'
        output = join(ndsi_dir,out_name)

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