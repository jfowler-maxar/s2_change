import os
from os.path import *
import subprocess

work_dir = r'E:\work\change_detect_solo'
gran = "T20LMR"
gran_dir = join(work_dir, gran)
chang_dir = join(gran_dir, 'change')
bnum = '1'

sieve = r'C:\Program Files\QGIS 3.28.1\apps\Python39\Scripts\gdal_sieve.py'
'''
gdal_sieve.bat -st 2 -8 
-of GTiff 
input
output
'''
in_name = f'{gran}_b{bnum}_ch_tmp.tif'
in_path = join(chang_dir, in_name)
if not exists(in_path):
    print('oh no')
    exit()
out_name = f'{gran}_b{bnum}_ch.tif'
output_path = join(chang_dir, out_name)
cmd = ['python',sieve,'-st','2','-8','-mask',in_path,'-of', 'GTiff',in_path,output_path]
print(cmd)
subprocess.call(cmd,shell=True)
#os.remove(output_path)