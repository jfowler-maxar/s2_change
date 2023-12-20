import os
from os.path import *
#from osgeo import gdal
from normalize_dif_test import indicies

work_dir = r"E:\work\change_detect_solo"
gran = "T18SUJ"
gran_dir = join(work_dir,gran)
index_dir = join(gran_dir,'indicies')
if not exists(index_dir):
    os.mkdir(index_dir)
index = indicies(gran)

#create ndvi,ndwi,ndbi,msavi?, what else?
for date in os.listdir(gran_dir):
    if len(date) == 8 and date.startswith('2'):
        l1c_dir = join(gran_dir, date, 'MSIL1C')
        l2a_dir = join(gran_dir, date, 'MSIL2A')
        gran_date = gran + "_" + date
        masked_tif = join(gran_dir, date, gran_date + '_6band_masked.tif')

        ndvi_path = join(index_dir,gran_date + '_ndvi.tif')
        if not exists(ndvi_path):
            index.norm_dif(masked_tif, 3, 4,ndvi_path) #offical >0.2, i like higher >0.4

        ndwi_path = join(index_dir,gran_date + '_ndwi.tif')
        if not exists(ndwi_path):
            index.norm_dif(masked_tif, 4, 2, ndwi_path)# >0.2

        ndbi_path = join(index_dir, gran_date + '_ndbi.tif')
        if not exists(ndbi_path):
            index.norm_dif(masked_tif, 4, 5, ndbi_path)

        ndsi_path = join(index_dir, gran_date + '_ndsi.tif')
        if not exists(ndsi_path):
            index.norm_dif(masked_tif, 5, 2, ndsi_path)

        msavi_path = join(index_dir,gran_date+'_msavi.tif')
        if not exists(msavi_path):
            index.msavi_calc(masked_tif, 4, 3,msavi_path)
        print('{} is done creating indicies'.format(date))
print('All indicies done for {}'.format(gran))