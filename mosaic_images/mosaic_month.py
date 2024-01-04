import os
from os.path import *
from osgeo import gdal
import numpy as np
import shutil

work_dir = r'E:\work\change_detect_solo'
gran = "T37RBM"
gran_dir = join(work_dir, gran)
# don't need mosaic dir, will just use month's dir
# mosaic_dir = join(gran_dir, 'mosaic')

# go into every month dir, and extract all date_6band_masked.tif
# for now, lets just move them to the month dir
for month in os.listdir(gran_dir):
    if len(month) == 6 and month.startswith('2'):
        month_dir = join(gran_dir, month)
        final_mosaic = f'{gran}_{month}_mosaic.tif'
        final_mosaic_path = join(month_dir, final_mosaic)
        mo1 = f'{gran}_{month}_mosaic1.tif'
        mo2 = f'{gran}_{month}_mosaic2.tif'
        mo3 = f'{gran}_{month}_mosaic3.tif'
        mo4 = f'{gran}_{month}_mosaic4.tif'
        mo5 = f'{gran}_{month}_mosaic5.tif'
        mo6 = f'{gran}_{month}_mosaic6.tif'
        mo1_path = join(month_dir, mo1)
        mo2_path = join(month_dir, mo2)
        mo3_path = join(month_dir, mo3)
        mo4_path = join(month_dir, mo4)
        mo5_path = join(month_dir, mo5)
        mo6_path = join(month_dir, mo6)
        if not exists(final_mosaic_path):
            print('checking if mosaic of bands exists')
            if not exists(mo1_path):
                print(f'{mo1_path} DNE')
                exit()
            if not exists(mo2_path):
                print(f'{mo1} DNE')
                exit()
            if not exists(mo3_path):
                print(f'{mo1} DNE')
                exit()
            if not exists(mo4_path):
                print(f'{mo1} DNE')
                exit()
            if not exists(mo5_path):
                print(f'{mo1} DNE')
                exit()
            if not exists(mo6_path):
                print(f'{mo1} DNE')
                exit()
            print('build vrt for all mosaics, then gdalwarp')
            #idk if faster to do vrt->gdalwarp or just use osgeo...
            #test time later
            mo_lst = [mo1_path,mo2_path,mo3_path,mo4_path,mo5_path,mo6_path]
            vrt_tmp = f'{gran}_{month}_mosaic_tmp.vrt'
            vrt_tmp_path = join(month_dir, vrt_tmp)
            gdal.BuildVRT(vrt_tmp_path, mo_lst, separate='separate', resolution='highest')
            if exists(vrt_tmp_path) == False:
                print(f'welp something went wrong creating:,\n {final_mosaic_path} ')
                exit()

            gdal.Translate(final_mosaic_path, vrt_tmp_path, format='GTIFF', outputType=gdal.GDT_Int16)
