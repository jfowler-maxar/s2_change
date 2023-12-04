import os
from os.path import *
#from osgeo import gdal
from zipfile import ZipFile
import shutil

#L1C
#MTD_TL.xml
#IMG_DATA contains jp2s

#L2A#MTD_TL.xml meta data
#IMG_DATA\R[120]0m
#R20m has SCL_20m.jp2

#setup work dir's
work_dir = r"E:\work\change_detect_solo"
gran = "T18SUJ"
gran_dir = join(work_dir,gran)
for z in os.listdir(gran_dir):
    if z.endswith(".zip"):
        #print(z)
        date = z.split("_")[2][0:8]
        #print(date)
        date_dir = join(gran_dir,date)
        if os.path.exists(date_dir) ==False:
            print("creating {}".format(date_dir))
            os.mkdir(date_dir)
        if os.path.exists(join(date_dir,z[:-3]+"safe")) == False:
            with ZipFile(join(gran_dir,z),'r') as zObject:
                print("Unzipping: {}".format(z))
                zObject.extractall(date_dir)
            zObject.close()
        else:
            print("no need to unzip {}".format(z))
#copy files now from SAFE to L1C and L2A dir's
for date in os.listdir(gran_dir):
    if len(date) == 8 and date.startswith('2'):
        print("Going into {} dir's".format(date))
        date_dir = join(gran_dir, date)
        for i in os.listdir(date_dir):
            if i.endswith(".SAFE"):
                processing_level = i.split("_")[1]
                if processing_level == "MSIL1C":
                    print("create {} dir".format(processing_level))
                    processing_level_dir = join(date_dir,processing_level)
                    if os.path.exists(processing_level_dir) == False:
                        os.mkdir(processing_level_dir)
                    #now take jp2s and meta data files
                    #super long names for the .safe's...
                    safe_dir = join(date_dir,i)
                    GRANULE_dir = join(safe_dir,"GRANULE")
                    for j in os.listdir(GRANULE_dir):
                        j_dir = join(GRANULE_dir, j)
                    for k in os.listdir(j_dir):
                        if k.endswith(".xml"):
                            if os.path.exists(join(processing_level_dir, k)):
                                print("{} already exists, skip".format(k))
                            else:
                                shutil.copy(join(j_dir,k), join(processing_level_dir, k))
                        #IMG_DATA_dir = join(join(GRANULE_dir,j),"IMG_DATA")
                    IMG_DATA_dir = join(j_dir, "IMG_DATA")
                    for l1c in os.listdir(IMG_DATA_dir):
                        if l1c.endswith("B02.jp2"):
                            if os.path.exists(join(processing_level_dir,l1c)):
                                print("{} already exists, skip".format(l1c))
                            else:
                                shutil.copy(join(IMG_DATA_dir,l1c),join(processing_level_dir,l1c))
                        if l1c.endswith("B03.jp2"):
                            if os.path.exists(join(processing_level_dir, l1c)):
                                print("{} already exists, skip".format(l1c))
                            else:
                                shutil.copy(join(IMG_DATA_dir, l1c), join(processing_level_dir, l1c))
                        if l1c.endswith("B04.jp2"):
                            if os.path.exists(join(processing_level_dir, l1c)):
                                print("{} already exists, skip".format(l1c))
                            else:
                                shutil.copy(join(IMG_DATA_dir, l1c), join(processing_level_dir, l1c))
                        if l1c.endswith("B08.jp2"):
                            if os.path.exists(join(processing_level_dir, l1c)):
                                print("{} already exists, skip".format(l1c))
                            else:
                                shutil.copy(join(IMG_DATA_dir, l1c), join(processing_level_dir, l1c))
                        if l1c.endswith("B11.jp2"):
                            if os.path.exists(join(processing_level_dir, l1c)):
                                print("{} already exists, skip".format(l1c))
                            else:
                                shutil.copy(join(IMG_DATA_dir, l1c), join(processing_level_dir, l1c))
                        if l1c.endswith("B12.jp2"):
                            if os.path.exists(join(processing_level_dir, l1c)):
                                print("{} already exists, skip".format(l1c))
                            else:
                                shutil.copy(join(IMG_DATA_dir, l1c), join(processing_level_dir, l1c))
                        if l1c.endswith("B8A.jp2"):
                            if os.path.exists(join(processing_level_dir, l1c)):
                                print("{} already exists, skip".format(l1c))
                            else:
                                shutil.copy(join(IMG_DATA_dir, l1c), join(processing_level_dir, l1c))
                        if l1c.endswith("B10.jp2"):
                            if os.path.exists(join(processing_level_dir, l1c)):
                                print("{} already exists, skip".format(l1c))
                            else:
                                shutil.copy(join(IMG_DATA_dir, l1c), join(processing_level_dir, l1c))
                    print("Done with {}".format(IMG_DATA_dir))

                #now for L2A
                elif processing_level == "MSIL2A":
                    print("create {} dir".format(processing_level))
                    processing_level_dir = join(date_dir, processing_level)
                    if os.path.exists(processing_level_dir) == False:
                        os.mkdir(processing_level_dir)
                    # now take jp2s and meta data files
                    # super long names for the .safe's...
                    safe_dir = join(date_dir, i)
                    GRANULE_dir = join(safe_dir, "GRANULE")
                    for j in os.listdir(GRANULE_dir):
                        j_dir = join(GRANULE_dir,j)
                    for k in os.listdir(j_dir):
                        if k.endswith(".xml"):
                            if os.path.exists(join(processing_level_dir, k)):
                                print("{} already exists, skip".format(k))
                            else:
                                shutil.copy(join(j_dir,k), join(processing_level_dir, k))
                    IMG_DATA_dir = join(j_dir, "IMG_DATA")
                        #print(IMG_DATA_dir)
                    R10m_dir = join(IMG_DATA_dir,"R10m")
                    R20m_dir = join(IMG_DATA_dir, "R20m")
                    for l2a in os.listdir((R10m_dir)):
                        if l2a.endswith("B02_10m.jp2"):
                            if os.path.exists(join(processing_level_dir, l2a)):
                                print("{} already exists, skip".format(l2a))
                            else:
                                shutil.copy(join(R10m_dir, l2a), join(processing_level_dir, l2a))
                        if l2a.endswith("B03_10m.jp2"):
                            if os.path.exists(join(processing_level_dir, l2a)):
                                print("{} already exists, skip".format(l2a))
                            else:
                                shutil.copy(join(R10m_dir, l2a), join(processing_level_dir, l2a))
                        if l2a.endswith("B04_10m.jp2"):
                            if os.path.exists(join(processing_level_dir, l2a)):
                                print("{} already exists, skip".format(l2a))
                            else:
                                shutil.copy(join(R10m_dir, l2a), join(processing_level_dir, l2a))
                        if l2a.endswith("B08_10m.jp2"):
                            if os.path.exists(join(processing_level_dir, l2a)):
                                print("{} already exists, skip".format(l2a))
                            else:
                                shutil.copy(join(R10m_dir, l2a), join(processing_level_dir, l2a))
                    for l2a in os.listdir((R20m_dir)):
                        if l2a.endswith("B11_20m.jp2"):
                            if os.path.exists(join(processing_level_dir, l2a)):
                                print("{} already exists, skip".format(l2a))
                            else:
                                shutil.copy(join(R20m_dir, l2a), join(processing_level_dir, l2a))
                        if l2a.endswith("B12_20m.jp2"):
                            if os.path.exists(join(processing_level_dir, l2a)):
                                print("{} already exists, skip".format(l2a))
                            else:
                                shutil.copy(join(R20m_dir, l2a), join(processing_level_dir, l2a))
                        if l2a.endswith("SCL_20m.jp2"):
                            if os.path.exists(join(processing_level_dir, l2a)):
                                print("{} already exists, skip".format(l2a))
                            else:
                                shutil.copy(join(R20m_dir, l2a), join(processing_level_dir, l2a))
                    print("done with {}".format(IMG_DATA_dir))

#i could add a part to delete the .zip's, that's easy, but gonna hold on to them for now cause testing
#I'll go ahead and delete the .SAFE's cause why not
for date in os.listdir(gran_dir):
    if len(date) == 8 and date.startswith('2'):
        print("Going into {} dir's".format(date))
        date_dir = join(gran_dir, date)
        for i in os.listdir(date_dir):
            if i.endswith(".SAFE"):
                print('deleting {} .SAFEs'.format(date))
                shutil.rmtree(join(date_dir,i))

print("its done!")

