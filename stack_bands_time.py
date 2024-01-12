import os
from os.path import *
from osgeo import gdal

work_dir = r'D:\s2_change\tiles'
gran = "T49QDD"
gran_dir = join(work_dir, gran)
time_series_dir = join(gran_dir, 'time_series')

if not os.path.exists(time_series_dir):
    os.mkdir(time_series_dir)

print('creating tmp bands')
for month in os.listdir(gran_dir):
    if len(month) == 6 and month.startswith('2'):
        month_dir = join(gran_dir, month)
        gran_month = gran + "_" + month
        masked_tif = join(month_dir, gran_month + '_mosaic.tif')
        if not exists(masked_tif):
            print('no {}'.format(masked_tif))
            exit(100)
        b1_vrt = join(month_dir, gran + '_b1_tmp.vrt')
        if not exists(b1_vrt):
            print(f'creating tmp {b1_vrt}')
            gdal.BuildVRT(b1_vrt, masked_tif, bandList='1', resolution='highest')

        b2_vrt = join(month_dir, gran + '_b2_tmp.vrt')
        if not exists(b2_vrt):
            print('creating tmp b2_vrt')
            gdal.BuildVRT(b2_vrt, masked_tif, bandList='2', resolution='highest')

        b3_vrt = join(month_dir, gran + '_b3_tmp.vrt')
        if not exists(b3_vrt):
            print('creating tmp b3_vrt')
            gdal.BuildVRT(b3_vrt, masked_tif, bandList='3', resolution='highest')

        b4_vrt = join(month_dir, gran + '_b4_tmp.vrt')
        if not exists(b4_vrt):
            print('creating tmp b4_vrt')
            gdal.BuildVRT(b4_vrt, masked_tif, bandList='4', resolution='highest')

        b5_vrt = join(month_dir, gran + '_b5_tmp.vrt')
        if not exists(b5_vrt):
            print('creating tmp b5_vrt')
            gdal.BuildVRT(b5_vrt, masked_tif, bandList='5', resolution='highest')

        b6_vrt = join(month_dir, gran + '_b6_tmp.vrt')
        if not exists(b6_vrt):
            print('creating tmp b6_vrt')
            gdal.BuildVRT(b6_vrt, masked_tif, bandList='6', resolution='highest')

# create lists
print('putting tmp_bands in lists')
band_1_list = []
band_2_list = []
band_3_list = []
band_4_list = []
band_5_list = []
band_6_list = []
print(band_1_list)
for month in os.listdir(gran_dir):
    if len(month) == 6 and month.startswith('2'):
        for tmp in os.listdir(join(gran_dir, month)):
            if tmp.endswith('b1_tmp.vrt'):
                band_1_list.append(join(gran_dir, month, tmp))
            if tmp.endswith('b2_tmp.vrt'):
                band_2_list.append(join(gran_dir, month, tmp))
            if tmp.endswith('b3_tmp.vrt'):
                band_3_list.append(join(gran_dir, month, tmp))
            if tmp.endswith('b4_tmp.vrt'):
                band_4_list.append(join(gran_dir, month, tmp))
            if tmp.endswith('b5_tmp.vrt'):
                band_5_list.append(join(gran_dir, month, tmp))
            if tmp.endswith('b6_tmp.vrt'):
                band_6_list.append(join(gran_dir, month, tmp))

band_1_list.sort()
band_2_list.sort()
band_3_list.sort()
band_4_list.sort()
band_5_list.sort()
band_6_list.sort()
print('Done looping through months and creating lists')

b1_stack = join(time_series_dir, gran + "_b1_stack_tmp.vrt")
b2_stack = join(time_series_dir, gran + "_b2_stack_tmp.vrt")
b3_stack = join(time_series_dir, gran + "_b3_stack_tmp.vrt")
b4_stack = join(time_series_dir, gran + "_b4_stack_tmp.vrt")
b5_stack = join(time_series_dir, gran + "_b5_stack_tmp.vrt")
b6_stack = join(time_series_dir, gran + "_b6_stack_tmp.vrt")

# creating vrt band stacks for each band
print('create vrt band stacks (1 band for every month)')
if not exists(b1_stack):
    print('stacking b1 blue')
    gdal.BuildVRT(b1_stack, band_1_list, separate='separate', resolution='highest')
if not exists(b2_stack):
    print('stacking b2 green')
    gdal.BuildVRT(b2_stack, band_2_list, separate='separate', resolution='highest')
if not exists(b3_stack):
    print('stacking b3 red')
    gdal.BuildVRT(b3_stack, band_3_list, separate='separate', resolution='highest')
if not exists(b4_stack):
    print('stacking b4 nir')
    gdal.BuildVRT(b4_stack, band_4_list, separate='separate', resolution='highest')
if not exists(b5_stack):
    print('stacking b5 swir 1')
    gdal.BuildVRT(b5_stack, band_5_list, separate='separate', resolution='highest')
if not exists(b6_stack):
    print('stacking b6 swir 2')
    gdal.BuildVRT(b6_stack, band_6_list, separate='separate', resolution='highest')

# now create final tifs
print('gdal_translate to get tifs')
b1_stack_tif = join(time_series_dir, gran + "_b1_stack.tif")
b2_stack_tif = join(time_series_dir, gran + "_b2_stack.tif")
b3_stack_tif = join(time_series_dir, gran + "_b3_stack.tif")
b4_stack_tif = join(time_series_dir, gran + "_b4_stack.tif")
b5_stack_tif = join(time_series_dir, gran + "_b5_stack.tif")
b6_stack_tif = join(time_series_dir, gran + "_b6_stack.tif")
if not exists(b1_stack_tif):
    print('translating b1')
    gdal.Translate(b1_stack_tif, b1_stack, format='GTiff', outputType=gdal.GDT_Int16)
if not exists(b2_stack_tif):
    print('translating b2')
    gdal.Translate(b2_stack_tif, b2_stack, format='GTiff', outputType=gdal.GDT_Int16)
if not exists(b3_stack_tif):
    print('translating b3')
    gdal.Translate(b3_stack_tif, b3_stack, format='GTiff', outputType=gdal.GDT_Int16)
if not exists(b4_stack_tif):
    print('translating b4')
    gdal.Translate(b4_stack_tif, b4_stack, format='GTiff', outputType=gdal.GDT_Int16)
if not exists(b5_stack_tif):
    print('translating b5')
    gdal.Translate(b5_stack_tif, b5_stack, format='GTiff', outputType=gdal.GDT_Int16)
if not exists(b6_stack_tif):
    print('translating b6')
    gdal.Translate(b6_stack_tif, b6_stack, format='GTiff', outputType=gdal.GDT_Int16)

# done creating time series stacks of each band, probably not the most efficient
# now to go back and delete all the tmps
print('deleting all tmp files')
for month in os.listdir(gran_dir):
    if len(month) == 6 and month.startswith('2'):
        month_dir = join(gran_dir, month)
        gran_month = gran + "_" + month
        for tmp in os.listdir(month_dir):
            if tmp.endswith('tmp.vrt'):
                print('removing {}'.format(tmp))
                os.remove(join(month_dir, tmp))
for tmp in os.listdir(time_series_dir):
    if tmp.endswith('_tmp.vrt'):
        print('removing {}'.format(tmp))
        os.remove(join(time_series_dir, tmp))

print('all done!')
