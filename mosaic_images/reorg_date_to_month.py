import os
from os.path import *
import shutil

work_dir = r"E:\work\change_detect_solo"
gran = "T37RBM"
gran_dir = join(work_dir,gran)

#take date dirs and move them all into month dirs
#ex: 20230129 and 20230130 would both go into 202301
for date in os.listdir(gran_dir):
    if len(date) == 8 and date.startswith('2'):
        month = date[0:6]
        print(date)
        print(month)
        date_dir = join(gran_dir, date)
        month_dir = join(gran_dir,month,date)
        print(month_dir)
        #if not exists(month_dir):
        #    os.mkdir(month_dir)
        shutil.copytree(date_dir,month_dir)

        shutil.rmtree(date_dir)
