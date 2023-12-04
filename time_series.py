import os
from os.path import *
from osgeo import gdal
import numpy as np
import numpy.ma as ma

def get_geo_data(in_raster_path):
    ds = gdal.Open(in_raster_path)
    srs_prj1 = ds.GetProjection()
    geoTransform1 = ds.GetGeoTransform()
    x1 = ds.RasterXSize
    y1 = ds.RasterYSize
    ds = None
    return (srs_prj1,geoTransform1,x1,y1)

def do_raster_stats(array_stack,stat):
    #print('Doing dstack')
    #raster_stack = np.dstack(list_of_arrays)
    if stat=='std':
        print('calculating std raster')
        out_array = np.nanstd(array_stack, axis=2)
    elif stat=='mean':
        print('calculating mean raster')
        out_array = np.nanmean(array_stack, axis=2)
    elif stat=='median':
        print('calculating median raster')
        out_array = np.nanmedian(array_stack, axis=2)
    elif stat=='range':
        print('calculating range raster')
        max_array = np.nanmax(array_stack, axis=2)
        min_array = np.nanmin(array_stack, axis=2)
        out_array = max_array-min_array
    else:
        print('something wrong in do_raster_stats')
        exit(10)
    return(out_array)

def output_raster(output_path,x,y,geoTransform,srs_prj,out_array):
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
    dst_band.WriteArray(out_array)
    #dst_band.SetNoDataValue(-100)#i dont think i need to set nodata for the stat-rasters
    dst_ds = None

def run_all_stats(input_raster):
    gran = input_raster.split('\\')[-3]
    input_dir = "\\".join(input_raster.split('\\')[0:-2])
    output_dir = join(input_dir,'time_stats')
    if exists(output_dir)==False:
       os.mkdir(output_dir)
    stat = input_raster.split('_')[-2]
    mean_raster = join(output_dir,gran+"_"+stat+'_mean.tif')
    median_raster = join(output_dir,gran+"_"+stat+'_median.tif')
    std_rastar = join(output_dir,gran+"_"+stat+'_std.tif')
    range_raster = join(output_dir,gran+"_"+stat+'_range.tif')
    if not exists(mean_raster):
        srs_prj, geoTransform, x, y = get_geo_data(input_raster)
        ds = gdal.Open(input_raster)
        print('add raster bands as array')
        layers = []
        if input_raster.endswith('.vrt'):
            for i in range(1, ds.RasterCount + 1):
                # b3_nan = ma.masked_where(b3 == -9999, b3)
                band = ds.GetRasterBand(i).ReadAsArray().astype('float32')
                band_masked = ma.masked_where(band == -100, band)
                band_filled = band_masked.filled(np.nan)
                layers.append(band_filled)
        elif input_raster.endswith('.tif'):
            for i in range(1, ds.RasterCount + 1):
                # b3_nan = ma.masked_where(b3 == -9999, b3)
                band = ds.GetRasterBand(i).ReadAsArray().astype('float32')
                band_masked = ma.masked_where(band == -9999, band)
                band_filled = band_masked.filled(np.nan)
                layers.append(band_filled)
        ds = None
        print('done adding raster bands as arrays')
        print('Doing dstack')
        raster_stack = np.dstack(layers)
        out_array1=do_raster_stats(raster_stack,'mean')
        output_raster(mean_raster,x,y,geoTransform,srs_prj,out_array1)
        if not exists(median_raster):
            out_array1 = do_raster_stats(raster_stack,'median')
            output_raster(median_raster, x, y, geoTransform, srs_prj, out_array1)
        if not exists(std_rastar):
            out_array1 = do_raster_stats(raster_stack,'std')
            output_raster(std_rastar, x, y, geoTransform, srs_prj, out_array1)
        #if not exists(range_raster):
        #    out_array1 = do_raster_stats(raster_stack,'range')
        #    output_raster(range_raster, x, y, geoTransform, srs_prj, out_array1)
    elif exists(mean_raster):
        print('nice this already exists: \n{}'.format(mean_raster))
        print('assuming if mean raster exists, the others do, maybe go back and fix this')

def main(input_raster):
    print('kick off')
    run_all_stats(input_raster)

if __name__ == "__main__":
    work_dir = r"E:\work\change_detect_solo"
    gran = "T18SUJ"
    gran_dir = join(work_dir,gran)
    time_series_dir = join(gran_dir,'time_series')

    for index in os.listdir(time_series_dir):
        if index.endswith('stack.vrt'):
            main(join(time_series_dir,index))
            print('{}_{} done'.format(gran,index))
        if index.endswith('stack.tif'):
            main(join(time_series_dir,index))
            print('{}_{} done'.format(gran,index))

    print('Time stats done')