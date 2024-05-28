import json
import requests
import pandas as pd
import os
from os.path import *

work_dir = r'E:\work\change_detect_solo'
gran = "T20LMR"
gran_dir = join(work_dir,gran)
if not exists(work_dir):
    os.mkdir(work_dir)
if not exists(gran_dir):
    os.mkdir(gran_dir)
text_dir = join(gran_dir,'text')
if not exists(text_dir):
    os.mkdir(text_dir)
def get_access_token(username: str, password: str) -> str:
    data = {
        "client_id": "cdse-public",
        "username": username,
        "password": password,
        "grant_type": "password",
    }
    try:
        r = requests.post(
            "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
            data=data,
        )
        r.raise_for_status()
    except Exception as e:
        raise Exception(
            f"Access token creation failed. Reponse from the server was: {r.json()}"
        )
    return r.json()["access_token"]

access_token = get_access_token("username", "password")#input username and password
'''
start_date = "2023-01-01"
end_date = "2023-02-28"
data_collection = "SENTINEL-2"
productType = "MSIL2A"
cloudCover = "[0,30]"
gran = "T37RBM"
bbox = "36.02,27.93,37.01,28.86"#wgs84 coords

#json = requests.get(f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$filter=Collection/Name eq 'SENTINEL-2' and ContentDate/Start gt {start_date}T00:00:00.000Z and ContentDate/Start lt {end_date}T00:00:00.000Z").json()

json = requests.get("https://catalogue.dataspace.copernicus.eu/odata/v1/Products?"
                    f"$filter=contains(Name, '{gran}') and "
                    f"contains(Name, '{productType}') and "
                    f"Collection/Name eq '{data_collection}' and "
                    f"Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value lt 10.00) and "
                    f"ContentDate/Start gt {start_date}T00:00:00.000Z and "
                    f"ContentDate/Start lt {end_date}T00:11:00.000Z").json()

df = pd.DataFrame.from_dict(json['value'])

# Print only specific columns
columns_to_print = ['Name']
#print(df[columns_to_print].head())
print(df[columns_to_print].to_string)

'''
data_collection = "SENTINEL-2"
productType = "MSIL2A"
cloud_cover = '40'
for i in range(1,13):
    if i<9:
        start_date = f"2023-0{i}-01"
        end_date = f"2023-0{i + 1}-01"
    elif i>=10 and i <12:
        start_date = f"2023-{i}-01"
        end_date = f"2023-{i+1}-01"
    elif i == 12:
        start_date = f"2023-{i}-01"
        end_date = f"2023-{i}-31"
    print(start_date)
    print(end_date)
    json = requests.get("https://catalogue.dataspace.copernicus.eu/odata/v1/Products?"
                        f"$filter=contains(Name, '{gran}') and "
                        f"contains(Name, '{productType}') and "
                        f"Collection/Name eq '{data_collection}' and "
                        f"Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value lt {cloud_cover}.00) and "
                        f"ContentDate/Start gt {start_date}T00:00:00.000Z and "
                        f"ContentDate/Start lt {end_date}T00:11:00.000Z").json()

    df = pd.DataFrame.from_dict(json['value'])

    csv_out = join(text_dir,f'{gran}_2023_{str(i)}_list.csv')

    df.to_csv(csv_out)

csv_lst = []
for csv in os.listdir(text_dir):
    print(csv)
    csv_path = join(text_dir,csv)
    data = pd.read_csv(csv_path)
    csv_lst.append(data)

frame = pd.concat(csv_lst,axis=0,ignore_index=True)
#print(frame[['Id','Name']])

csv_out = join(text_dir, f'{gran}_id.csv')

frame.to_csv(csv_out, columns=['Id','Name'])
