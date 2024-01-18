import os
from os.path import *
from osgeo import gdal
import numpy as np
import numpy.ma as ma

work_dir = r"E:\work\change_detect_solo"
gran = "T18SUJ"
gran_dir = join(work_dir, gran)
time_series_dir = join(gran_dir, 'time_series')
temporal_slope_dir = join(gran_dir, 'temp_slope')
if not exists(temporal_slope_dir):
    os.mkdir(temporal_slope_dir)

###Set up y variable for linear regression
# test with just b1 stack
b1_stack = join(time_series_dir, 'T18SUJ_b1_stack.tif')
ds = gdal.Open(b1_stack)
srs_prj = ds.GetProjection()
geoTransform = ds.GetGeoTransform()
x = ds.RasterXSize
y = ds.RasterYSize
print('Going through stack \n{}'.format(b1_stack))
array_layers = []
for i in range(1, ds.RasterCount + 1):
    print("layer number: {}".format(i))
    # b3_nan = ma.masked_where(b3 == -9999, b3)
    band = ds.GetRasterBand(i).ReadAsArray().astype('float32')
    #band_masked = ma.masked_where(band == -9999, band)
    #band_filled = band_masked.filled(np.nan)
    array_layers.append(band)
ds = None

#make avg arrary to sub in if nan
avg_arr = np.nanmean(array_layers)
###set up model
print('set up model')
n = len(array_layers)
seed = (n*n*n)-n #not sure what this is for
for i in range(len(array_layers)):
    print(i)
    coef = (12*(i)-((6*n)+(6*1)))/seed
    # where -9999 got to avg, otherwise use array layer
    in_arr = np.where(array_layers[i] == -9999, avg_arr, array_layers[i])
    #multiply raster by coefficient
    if i == 0:
        print('first iteration of raster*coef')
        outSlope = in_arr*coef
    else:
        outSlope = outSlope+(in_arr*coef)

print('Creating final tempslope.tif')
output_path = join(temporal_slope_dir, 'b1_tempslope.tif')
drv = gdal.GetDriverByName("GTiff")
dst_ds = drv.Create(output_path,
                    x,
                    y,
                    1,
                    gdal.GDT_Int16,
                    )
dst_ds.SetGeoTransform(geoTransform)
dst_ds.SetProjection(srs_prj)
dst_band = dst_ds.GetRasterBand(1)
dst_band.WriteArray(outSlope)
# dst_band.SetNoDataValue(-100)
dst_ds = None
