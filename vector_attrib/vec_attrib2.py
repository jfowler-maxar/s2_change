import os
from os.path import *
import fiona, rasterio
import geopandas as gpd
from rasterio.plot import show
import matplotlib.pyplot as plt
import rasterio.plot as rplt
from rasterio.features import rasterize
from rasterstats import zonal_stats


def enum_items(source):
    print("\n")
    for ele in enumerate(source):
        print(ele)


def list_columns(df):
    field_list = list(df)
    enum_items(field_list)
    return field_list


# For loading feature classes into geopandas dataframe
def loadfc_as_gpd(fgdb):
    layers = fiona.listlayers(fgdb)
    enum_items(layers)
    index = int(input("Which index to load? "))
    fcgpd = gpd.read_file(fgdb, layer=layers[index])
    return fcgpd


# For loading shapefiles into geopandas dataframe
def loadshp_as_gpd(shp):
    data = gpd.read_file(shp)
    return data


# For optional filtering of data
def filter_gpd(fcgpd):
    field_list = list_columns(fcgpd)
    index = int(input("Filter by which field (index)? "))
    field = field_list[index]
    value = input("Enter value: ")
    result = fcgpd[fcgpd[field] == value]
    return result


# For re-projecting input vector layer to raster projection (Rasterio v. 1.0.22)
def reproject(fcgpd, raster):
    proj = raster.crs.to_proj4()
    print("Original vector layer projection: ", fcgpd.crs)
    reproj = fcgpd.to_crs(proj)
    print("New vector layer projection (PROJ4): ", reproj.crs)
    fig, ax = plt.subplots(figsize=(15, 15))
    rplt.show(raster, ax=ax)
    reproj.plot(ax=ax, facecolor='none', edgecolor='red')
    fig.show()
    return reproj


# For dissolving geopandas dataframe by selected field
def dissolve_gpd(df):
    field_list = list_columns(df)
    index = int(input("Dissolve by which field (index)? "))
    dgpd = df.dissolve(by=field_list[index])
    return dgpd


# For selecting which raster statistics to calculate
def stats_select():
    stats_list = ['min', 'max', 'mean', 'count',
                  'sum', 'std', 'median', 'majority',
                  'minority', 'unique', 'range']
    enum_items(stats_list)
    indices = input("Enter raster statistics selections separated by space: ")
    stats = list(indices.split())
    out_stats = list()
    for i in stats:
        out_stats.append(stats_list[int(i)])
    return out_stats


# For calculating zonal statistics
def get_zonal_stats(vector, raster, stats):
    # Run zonal statistics, store result in geopandas dataframe
    result = zonal_stats(vector, raster, stats=stats, geojson_out=True)
    geostats = gpd.GeoDataFrame.from_features(result)
    return geostats


# For generating raster from zonal statistics result
def stats_to_raster(zdf, raster, stats, out_raster, no_data='y'):
    meta = raster.meta.copy()
    out_shape = raster.shape
    transform = raster.transform
    dtype = raster.dtypes[0]
    field_list = list_columns(stats)
    index = int(input("Rasterize by which field? "))
    zone = zdf[field_list[index]]
    shapes = ((geom, value) for geom, value in zip(zdf.geometry, zone))
    burned = rasterize(shapes=shapes, fill=0, out_shape=out_shape, transform=transform)
    show(burned)
    meta.update(dtype=rasterio.float32, nodata=0)
    # Optional to set nodata values to min of stat
    if no_data == 'y':
        cutoff = min(zone.values)
        print("Setting nodata cutoff to: ", cutoff)
        burned[burned < cutoff] = 0
    with rasterio.open(out_raster, 'w', **meta) as out:
        out.write_band(1, burned)
    print("Zonal Statistics Raster generated")


def main():
    work_dir = r'E:\work\change_detect_solo'
    gran = "T20LMR"
    gran_dir = join(work_dir, gran)
    change_dir = join(gran_dir, 'change')
    time_stats_dir = join(gran_dir, 'time_stats')
    vec_dir = join(gran_dir, 'vec')

    bnum = '1'
    in_name = f'{gran}_b{bnum}_ch_tmp.shp'
    in_shp = join(vec_dir, in_name)
    out_test = f'{gran}_b{bnum}_ch_test2.shp'
    out_shp = join(vec_dir, out_test)

    ts_std_file = join(change_dir, f'{gran}_b{bnum}_stacktempslope_std.tif')

    rst = ts_std_file
    raster = rasterio.open(rst)

    fgdb = in_shp
    vector = loadfc_as_gpd(fgdb)

    p_vector = reproject(vector, raster)

    d_vector = dissolve_gpd(p_vector)
    out_rst = out_shp
    stats_to_get = stats_select()

    zs = get_zonal_stats(d_vector, rst, stats_to_get)
    stats_to_raster(zs, raster, stats_to_get, out_rst)

if __name__ == '__main__':
    main()