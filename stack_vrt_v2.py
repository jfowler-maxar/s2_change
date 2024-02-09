import os
from os.path import *
from osgeo import gdal
import numpy as np

work_dir = r'E:\work\change_detect_solo'
gran = "T52SBJ"
gran_dir = join(work_dir,gran)

#create 6band_stack
for month in os.listdir(gran_dir):
    if len(month) == 6 and month.startswith('2'):
        #D:\s2_change\tiles\T49QDD\202302\20230226
        #print(join(gran_dir,month))
        month_dir = join(gran_dir,month)
        for date in os.listdir(month_dir):
            if len(date) == 8 and date.startswith('2'):
                date_dir = join(month_dir,date)
                l2a_dir = join(date_dir, 'MSIL2A')
                jp2_list = []
                gran_date = gran + "_" + date
                dst_6band = join(date_dir, gran_date + '_6band.vrt')
                if exists(l2a_dir) == False:
                    print('MSIL2A dir does not exist! Cant do anything')
                    exit(2)
                if exists(l2a_dir):
                    print('running 6band stack on L2A')
                    for jp2 in os.listdir(l2a_dir):
                        if jp2.endswith('.jp2'):
                            if jp2.endswith('B02_10m.jp2'):
                                jp2_list.append(join(l2a_dir, jp2))
                            elif jp2.endswith('B03_10m.jp2'):
                                jp2_list.append(join(l2a_dir, jp2))
                            elif jp2.endswith('B04_10m.jp2'):
                                jp2_list.append(join(l2a_dir, jp2))
                            elif jp2.endswith('B08_10m.jp2'):
                                jp2_list.append(join(l2a_dir, jp2))
                            elif jp2.endswith('B11_20m.jp2'):
                                jp2_list.append(join(l2a_dir, jp2))
                            elif jp2.endswith('B12_20m.jp2'):
                                jp2_list.append(join(l2a_dir, jp2))
                            elif jp2.endswith('SCL_20m.jp2'):#grab scl for cloud mask
                                scl = join(l2a_dir, jp2)
                    jp2_list.sort()
                    #print(jp2_list)
                    print('Creating ' + dst_6band)
                    gdal.BuildVRT(dst_6band, jp2_list, separate='separate', resolution='highest')
                    if exists(dst_6band) == False:
                        print('welp something went wrong')
                        exit(4)

#run through again cause too messy
#gonna attempt to grab b10
#will point to scl and newly create 6band.vrt

for month in os.listdir(gran_dir):
    if len(month) == 6 and month.startswith('2'):
        #D:\s2_change\tiles\T49QDD\202302\20230226
        #print(join(gran_dir,month))
        month_dir = join(gran_dir,month)
        for date in os.listdir(month_dir):
            if len(date) == 8 and date.startswith('2'):
                date_dir = join(month_dir,date)
                l2a_dir = join(date_dir, 'MSIL2A')
                l1c_dir = join(date_dir, 'MSIL1C')
                jp2_list = []
                gran_date = gran + "_" + date
                dst_6band = join(date_dir, gran_date + '_6band.vrt')
                print('Starting masking for {}'.format(dst_6band))
                masked_tif = join(month_dir, gran_date + '_6band_masked.tif')  # would just be copied later...
                if not exists(masked_tif):
                    if exists(dst_6band) == False:
                        print('SHITTTT')
                        print('{} not found'.format(dst_6band))
                        exit(11)
                    if exists(l1c_dir) == False:
                        print('MSIL1C dir does not exist!')
                        print('no b10 for cloud masking oh well')
                    elif exists(l1c_dir):
                        print('MSIL1C exits, grabbing b10')
                        for jp2 in os.listdir(l1c_dir):
                            if jp2.endswith('.jp2'):
                                if jp2.endswith('B10.jp2'):
                                    b10_path = join(l1c_dir,jp2)

                    for jp2 in os.listdir(l2a_dir):
                        if jp2.endswith('SCL_20m.jp2'):
                            scl = join(l2a_dir, jp2)#for cloud masks

                    print('Open scl')
                    scl_file = gdal.Open(scl)
                    scl_class = scl_file.GetRasterBand(1)
                    scl_x = scl_class.XSize*2
                    scl_y = scl_class.YSize*2
                    scl_class = scl_class.ReadAsArray(buf_xsize=scl_x,buf_ysize=scl_y).astype('uint16')
                    #scl classes for the mask: Nodata(0),Saturated(1),cloudshadows(3),cloud med (8), cloud high (9)
                    scl_file = None
                    print('Open vrt')
                    vrt_file = gdal.Open(dst_6band)
                    srs_prj = vrt_file.GetProjection()
                    geoTransform = vrt_file.GetGeoTransform()
                    x = vrt_file.RasterXSize
                    y = vrt_file.RasterYSize
                    print('vrt get raster bands!')
                    vrt_b1 = vrt_file.GetRasterBand(1).ReadAsArray().astype('uint16')
                    vrt_b2 = vrt_file.GetRasterBand(2).ReadAsArray().astype('uint16')
                    vrt_b3 = vrt_file.GetRasterBand(3).ReadAsArray().astype('uint16')
                    vrt_b4 = vrt_file.GetRasterBand(4).ReadAsArray().astype('uint16')
                    vrt_b5 = vrt_file.GetRasterBand(5).ReadAsArray().astype('uint16')
                    vrt_b6 = vrt_file.GetRasterBand(6).ReadAsArray().astype('uint16')
                    vrt_file = None
                    print('SCL class simplification')
                    #mask = np.where(scl_class==1 or scl_class==3 or scl_class==8 or scl_clas==9,scl_class,0)
                    mask1 = np.where(scl_class==1 ,0,scl_class)
                    mask2 = np.where(mask1==3,0,mask1)
                    mask3 = np.where(mask2==8,0,mask2)
                    mask4 = np.where(mask3==9,0,mask3)
                    mask5 = np.where(mask4!=0,1,mask4)
                    #set 0 to -9999, because I want nodata to be -9999 (if it's nodata=0 later things getting annoying)
                    mask6 = np.where(mask5==0,-9999,mask5)
                    scl_class, mask1, mask2, mask3, mask4, mask5 = None, None, None, None, None, None
                    print('SCL masking vrt')
                    clip1 = np.where(mask6==1,vrt_b1,-9999)
                    clip2 = np.where(mask6==1,vrt_b2,-9999)
                    clip3 = np.where(mask6 == 1, vrt_b3,-9999)
                    clip4 = np.where(mask6 == 1, vrt_b4,-9999)
                    clip5 = np.where(mask6 == 1, vrt_b5,-9999)
                    clip6 = np.where(mask6 == 1, vrt_b6,-9999)
                    vrt_b1, vrt_b2, vrt_b3, vrt_b4, vrt_b5, vrt_b6 = None, None, None, None, None, None

                    print('creating {}'.format(masked_tif))
                    drv = gdal.GetDriverByName("GTiff")
                    dst_ds = drv.Create(masked_tif,
                                        x,
                                        y,
                                        6,
                                        gdal.GDT_Int16
                                        )
                    dst_ds.SetGeoTransform(geoTransform)
                    dst_ds.SetProjection(srs_prj)
                    dst_band = dst_ds.GetRasterBand(1)
                    dst_band.WriteArray(clip1)
                    dst_band.SetNoDataValue(-9999)
                    clip1 = None
                    dst_band = dst_ds.GetRasterBand(2)
                    dst_band.WriteArray(clip2)
                    dst_band.SetNoDataValue(-9999)
                    clip2 = None
                    dst_band = dst_ds.GetRasterBand(3)
                    dst_band.WriteArray(clip3)
                    dst_band.SetNoDataValue(-9999)
                    clip3 = None
                    dst_band = dst_ds.GetRasterBand(4)
                    dst_band.WriteArray(clip4)
                    dst_band.SetNoDataValue(-9999)
                    clip4 = None
                    dst_band = dst_ds.GetRasterBand(5)
                    dst_band.WriteArray(clip5)
                    dst_band.SetNoDataValue(-9999)
                    clip5 = None
                    dst_band = dst_ds.GetRasterBand(6)
                    dst_band.WriteArray(clip6)
                    dst_band.SetNoDataValue(-9999)
                    dst_ds = None
                    #now i can use 6 band stack to create ndvi, ndbi,msavi, whatever i want
