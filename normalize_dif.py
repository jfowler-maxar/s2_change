from osgeo import gdal
import numpy as np
import numpy.ma as ma


class indicies():

    def __init__(self, granule):
        self.gran = granule
        print('Working on ' + self.gran)

    def set_chip(self, input_path, in_x, in_y):
        # assuming s2, 10980x10980
        # input
        in_ds = gdal.Open(input_path)
        geoTransform = in_ds.GetGeoTransform()
        in_ds = None
        chip_x = int(in_x)
        chip_y = int(in_y)
        minx = geoTransform[0]
        miny = geoTransform[3]
        step_x = geoTransform[1]
        step_y = geoTransform[5]

        return chip_x, chip_y, minx, miny, step_x, step_y

    def norm_dif(self, input_path, band_red, band_nir, out_path):
        """take multibanded-raster file location, band numbers(int's), and output path
        I think of it in terms of ndvi, so using "red" and "nir"
        also cause use ndvi all the time, just gonna set that as the default
        open and close gdal files, output to whatever location specified
        DOES NOT account for sentinel 2 jan 2022 changes,
        so manipulate that (-1000) before if pre jan 2022
        put it on -100,100 scale
        """
        in_ds = gdal.Open(input_path)
        srs_prj = in_ds.GetProjection()
        geoTransform = in_ds.GetGeoTransform()
        xsize = ds.RasterXSize
        ysize = ds.RasterYSize


        b3 = in_ds.GetRasterBand(band_red).ReadAsArray().astype('float32')
        b4 = in_ds.GetRasterBand(band_nir).ReadAsArray().astype('float32')
        in_ds = None

        drv = gdal.GetDriverByName("GTiff")
        dst_ds = drv.Create(out_path,
                            xsize,
                            ysize,
                            1,
                            gdal.GDT_Int16,
                            options=["TILED=YES", "BLOCKXSIZE=256",
                                     "BLOCKYSIZE=256"]
                            )
        dst_ds.SetGeoTransform(geoTransform)
        dst_ds.SetProjection(srs_prj)
        dst_band = dst_ds.GetRasterBand(1)

        chip_x, chip_y, minx, miny, step_x, step_y = self.set_chip(input_path, 512, 512)
        count_x = 0
        count_y = 0

        for x in range(0, xsize, chip_x):
            print(x)
            if x + chip_x < xsize:
                cols = chip_x
                x_off = minx + (count_x * step_x)
                count_x = count_x + chip_x
            else:
                cols = xsize - x
                x_off = minx + (count_x * step_x)
                count_x = count_x + x
            count_y = 0
            for y in range(0, ysize, chip_y):
                if y + chip_y < ysize:
                    rows = chip_y
                    y_off = miny + (count_y * step_y)
                    count_y = count_y + chip_y
                else:
                    rows = ysize - y
                    y_off = miny + (count_y * step_y)
                    count_y = count_y + y

                # need to ignore no data, 0 in masked.tif
                # masked_data = ma.masked_where(data == ndv, data)
                b3_nan = ma.masked_where(b3 == -9999, b3)
                b4_nan = ma.masked_where(b4 == -9999, b4)
                # -1000 post jan 2022 to make it equal/comparable to pre jan 2022...
                # calc = ((b4 - 1000) - (b3 - 1000) + .0001) / ((b4 - 1000) + (b3 - 1000) + .0001) * 100
                calc = ((b4_nan) - (b3_nan)) / ((b4_nan) + (b3_nan) + .0001) * 100
                # index < |1| is going to no data
                round_to_int = np.rint(calc)
                clamp_neg_100 = np.where(round_to_int >= -100, round_to_int, -100)
                clamp_over_100 = np.where(clamp_neg_100 <= 100, clamp_neg_100, 100)  # clamp to -100 and 100
                dst_band.WriteArray(clamp_over_100,x,y)
        dst_band.SetNoDataValue(-100)

        dst_ds = None
        print('"normalize_dif done for "{}'.format(out_path))

    def msavi_calc(self, input_path, band_nir, band_red, out_path):
        in_ds = gdal.Open(input_path)
        srs_prj = in_ds.GetProjection()
        geoTransform = in_ds.GetGeoTransform()
        xsize = in_ds.RasterXSize
        ysize = in_ds.RasterYSize

        b3 = in_ds.GetRasterBand(band_red).ReadAsArray().astype('float32')
        b4 = in_ds.GetRasterBand(band_nir).ReadAsArray().astype('float32')
        in_ds = None

        drv = gdal.GetDriverByName("GTiff")
        dst_ds = drv.Create(out_path,
                            xsize,
                            ysize,
                            1,
                            gdal.GDT_Int16,
                            options=["TILED=YES", "BLOCKXSIZE=256",
                                     "BLOCKYSIZE=256"]
                            )
        dst_ds.SetGeoTransform(geoTransform)
        dst_ds.SetProjection(srs_prj)
        dst_band = dst_ds.GetRasterBand(1)

        chip_x, chip_y, minx, miny, step_x, step_y = self.set_chip(input_path, 256, 256)
        count_x = 0
        count_y = 0

        for x in range(0, xsize, chip_x):
            print(x)
            if x + chip_x < xsize:
                cols = chip_x
                x_off = minx + (count_x * step_x)
                count_x = count_x + chip_x
            else:
                cols = xsize - x
                x_off = minx + (count_x * step_x)
                count_x = count_x + x
            count_y = 0
            for y in range(0, ysize, chip_y):
                if y + chip_y < ysize:
                    rows = chip_y
                    y_off = miny + (count_y * step_y)
                    count_y = count_y + chip_y
                else:
                    rows = ysize - y
                    y_off = miny + (count_y * step_y)
                    count_y = count_y + y

                b3_nan = ma.masked_where(b3 == -9999, b3)
                b4_nan = ma.masked_where(b4 == -9999, b4)

                # MSAVI2 = (1/2) * (2 * (NIR +1) - sqrt((2 * NIR + 1)^2-8(NIR - Red)))
                calc = (1 / 2) * (2 * (b4_nan + 1) - np.sqrt(((2 * b4_nan + 1) ** 2) - 8 * (b4_nan - b3_nan)))
                scale_100 = calc * 100
                round_to_int = np.rint(scale_100)
                clamp_neg_100 = np.where(round_to_int >= -100, round_to_int, -100)
                clamp_over_100 = np.where(round_to_int <= 100, round_to_int, 100)  # clamp to -100 and 100
                dst_band.WriteArray(clamp_over_100,x,y)
        dst_ds = None
        print("msavi done for {}".format(out_path))
