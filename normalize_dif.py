from osgeo import gdal
import numpy as np
import numpy.ma as ma

class indicies():
    def norm_dif(img_path,band_red,band_nir,out_path):
        """take multibanded-raster file location, band numbers(int's), and output path
        I think of it in terms of ndvi, so using "red" and "nir"
        also cause use ndvi all the time, just gonna set that as the default
        open and close gdal files, output to whatever location specified
        DOES NOT account for sentinel 2 jan 2022 changes,
        so manipulate that (-1000) before if pre jan 2022
        put it on -100,100 scale
        """
        img_file = gdal.Open(img_path)
        srs_prj = img_file.GetProjection()
        geoTransform = img_file.GetGeoTransform()
        x = img_file.RasterXSize
        y = img_file.RasterYSize
        b3 = img_file.GetRasterBand(band_red).ReadAsArray().astype('float32')
        b4 = img_file.GetRasterBand(band_nir).ReadAsArray().astype('float32')
        img_file = None

        #need to ignore no data, 0 in masked.tif
        #masked_data = ma.masked_where(data == ndv, data)
        b3_nan = ma.masked_where(b3==-9999,b3)
        b4_nan = ma.masked_where(b4 ==-9999, b4)
        #-1000 post jan 2022 to make it equal/comparable to pre jan 2022...
        #calc = ((b4 - 1000) - (b3 - 1000) + .0001) / ((b4 - 1000) + (b3 - 1000) + .0001) * 100
        calc = ((b4_nan) - (b3_nan)) / ((b4_nan) + (b3_nan) + .0001) * 100
        # index < |1| is going to no data
        round_to_int = np.rint(calc)
        clamp_neg_100 = np.where(round_to_int >= -100,round_to_int,-100)
        clamp_over_100 = np.where(clamp_neg_100 <= 100,clamp_neg_100,100) #clamp to -100 and 100

        drv = gdal.GetDriverByName("GTiff")
        dst_ds = drv.Create(out_path,
                            x,
                            y,
                            1,
                            gdal.GDT_Int16,
                            )
        dst_ds.SetGeoTransform(geoTransform)
        dst_ds.SetProjection(srs_prj)
        dst_band = dst_ds.GetRasterBand(1)
        dst_band.WriteArray(clamp_over_100)
        dst_band.SetNoDataValue(-100)
        dst_ds = None
        print('"normalize_dif done for "{}'.format(out_path))

    def msavi_calc(img_path,band_nir,band_red,out_path):
        img_file = gdal.Open(img_path)
        srs_prj = img_file.GetProjection()
        geoTransform = img_file.GetGeoTransform()
        x = img_file.RasterXSize
        y = img_file.RasterYSize
        b3 = img_file.GetRasterBand(band_red).ReadAsArray().astype('float32')
        b4 = img_file.GetRasterBand(band_nir).ReadAsArray().astype('float32')
        img_file = None

        b3_nan = ma.masked_where(b3 ==-9999, b3)
        b4_nan = ma.masked_where(b4 ==-9999, b4)

        #MSAVI2 = (1/2) * (2 * (NIR +1) - sqrt((2 * NIR + 1)^2-8(NIR - Red)))
        calc =(1/2) * (2 * (b4_nan + 1) - np.sqrt(((2 * b4_nan + 1)**2) - 8 * (b4_nan - b3_nan)))
        scale_100 = calc*100
        round_to_int = np.rint(scale_100)
        clamp_neg_100 = np.where(round_to_int >= -100, round_to_int, -100)
        clamp_over_100 = np.where(round_to_int <= 100, round_to_int, 100)  # clamp to -100 and 100

        drv = gdal.GetDriverByName("GTiff")
        dst_ds = drv.Create(out_path,
                            x,
                            y,
                            1,
                            gdal.GDT_Int16,
                            )
        dst_ds.SetGeoTransform(geoTransform)
        dst_ds.SetProjection(srs_prj)
        dst_band = dst_ds.GetRasterBand(1)
        dst_band.WriteArray(clamp_over_100)
        dst_ds = None
        print("msavi done for {}".format(out_path))