import os
from os.path import *
#from osgeo import gdal
from normalize_dif import indicies

work_dir = r"E:\work\change_detect_solo"
gran = "T20LMR"
gran_dir = join(work_dir,gran)

#create ndvi,ndwi,ndbi,msavi?, what else?
#ndvi first cause it's easy
for month in os.listdir(gran_dir):
    if len(month) == 6 and month.startswith('2'):
        gran_month = gran + "_" + month
        masked_tif = join(gran_dir, month, gran_month + '_min_mosaic.tif')
        print(masked_tif)
        create_index = indicies(gran)

        ndvi_path = join(gran_dir,month,gran_month + '_ndvi.tif')
        if exists(ndvi_path) == False:
            create_index.norm_dif(masked_tif, 3, 4,ndvi_path) #offical >0.2, i like higher >0.4

        ndwi_path = join(gran_dir,month,gran_month + '_ndwi.tif')
        if exists(ndwi_path) == False:
            create_index.norm_dif(masked_tif, 4, 2, ndwi_path)# >0.2

        ndbi_path = join(gran_dir, month, gran_month + '_ndbi.tif')
        if exists(ndbi_path) == False:
            create_index.norm_dif(masked_tif, 4, 5, ndbi_path)
        '''
        ndsi_path = join(gran_dir, month, gran_month + '_ndsi.tif')
        if exists(ndsi_path) == False:
            create_index.norm_dif(masked_tif, 5, 2, ndsi_path)
        '''
        msavi_path = join(gran_dir,month,gran_month+'_msavi.tif')
        if exists(msavi_path) == False:
            create_index.msavi_calc(masked_tif, 4, 3,msavi_path)
        print('{} is done creating indicies'.format(month))
print('All indicies done for {}'.format(gran))