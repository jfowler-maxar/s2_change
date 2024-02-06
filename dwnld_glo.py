import os
from os.path import *
from osgeo import gdal
import fiona
from shapely.geometry import Polygon, mapping, shape
import subprocess

#run in texveg conda env

work_dir = r"E:\work\change_detect_solo"
glo30_dir = r"E:\work\dem\glo30"
gran = "T36RYS"
gran_dir = join(work_dir,gran)
if not exists(gran_dir):
    os.mkdir(gran_dir)
gran = gran[1:]

s2_grid_shp = r"E:\work\grid\s2_grid\Sentinel-2-Shapefile-Index-master\sentinel_2_index_shapefile.shp"
srtm_1x1_shp = r"E:\work\grid\srtm_grid_1deg\srtm_grid_1deg.shp"

with fiona.open(s2_grid_shp) as input:
    meta = input.meta
    for feature in input:
        if feature['properties']['Name'] == gran:
            #geom = feature['geometry']
            #extent = shape(geom).bounds
            #print(extent)
            aoiGeom = Polygon(feature['geometry']['coordinates'][0])
            print(aoiGeom)

polyShp = fiona.open(srtm_1x1_shp)
polyList = []
polyProperties = []
id_lst = []
for poly in polyShp:
    polyGeom = Polygon(poly['geometry']['coordinates'][0])
    polyList.append(polyGeom)
    polyProperties.append(poly['properties'])
    id_lst.append(poly['properties']['id'])

clip_lst = []
clip_prop = []
clip_id = [] #this is what I want, for grabbing geocell names

for index, poly in enumerate(polyList):
    result = aoiGeom.intersection(poly)
    if result.area:
        clip_lst.append(result)
        clip_prop.append(polyProperties[index])
        clip_id.append(id_lst[index])

#print(clip_id)

dem_lst = []
for i in range(len(clip_id)):
    geocell = clip_id[i]
    print(geocell)
    geocell_dir = join(glo30_dir,geocell)
    if not exists(geocell_dir):
        os.mkdir(geocell_dir)
    ns = geocell[0:3]
    ew = geocell[3:]
    #print(f'Copernicus_DSM_COG_10_{ns}_00_{ew}_00_DEM.tif')
    dem_name = f'Copernicus_DSM_COG_10_{ns}_00_{ew}_00_DEM'
    dem_final_path = join(geocell_dir,dem_name+'.tif')
    dem_lst.append(dem_final_path)
    if os.path.isfile(dem_final_path):
        print(f'{dem_final_path} exists')
    else:
        cmd = f'aws s3 cp --no-sign-request s3://copernicus-dem-30m/{dem_name}/ {geocell_dir}\ --recursive --exclude "*" --include "*DEM.tif'
        #print(cmd)
        #subprocess.run(cmd)
        os.system(cmd)


gran_dem = join(gran_dir,"T"+gran+"_glo30_buf.tif")
input_ds = []
for f in dem_lst:
    ds = gdal.Open(f)
    input_ds.append(ds)

gdal.Warp(gran_dem,input_ds,
          format="GTiff",
          outputType=gdal.GDT_Float32
          )