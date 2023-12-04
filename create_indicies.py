import os
from os.path import *
#from osgeo import gdal
from normalize_dif import indicies

work_dir = r"E:\work\change_detect_solo"
gran = "T18SUJ"
gran_dir = join(work_dir,gran)

#create ndvi,ndwi,ndbi,msavi?, what else?
#ndvi first cause it's easy
for date in os.listdir(gran_dir):
    if len(date) == 8 and date.startswith('2'):
        l1c_dir = join(gran_dir, date, 'MSIL1C')
        l2a_dir = join(gran_dir, date, 'MSIL2A')
        gran_date = gran + "_" + date
        masked_tif = join(gran_dir, date, gran_date + '_6band_masked.tif')

        ndvi_path = join(gran_dir,date,gran_date + '_ndvi.tif')
        if exists(ndvi_path) == False:
            indicies.norm_dif(masked_tif, 3, 4,ndvi_path) #offical >0.2, i like higher >0.4

        ndwi_path = join(gran_dir,date,gran_date + '_ndwi.tif')
        if exists(ndwi_path) == False:
            indicies.norm_dif(masked_tif, 4, 2, ndwi_path)# >0.2

        ndbi_path = join(gran_dir, date, gran_date + '_ndbi.tif')
        if exists(ndbi_path) == False:
            indicies.norm_dif(masked_tif, 4, 5, ndbi_path)

        ndsi_path = join(gran_dir, date, gran_date + '_ndsi.tif')
        if exists(ndsi_path) == False:
            indicies.norm_dif(masked_tif, 5, 2, ndsi_path)

        msavi_path = join(gran_dir,date,gran_date+'_msavi.tif')
        if exists(msavi_path) == False:
            indicies.msavi_calc(masked_tif, 4, 3,msavi_path)
        print('{} is done creating indicies'.format(date))
print('All indicies done for {}'.format(gran))