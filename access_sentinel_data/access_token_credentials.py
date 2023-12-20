import json
import requests


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


access_token = get_access_token("fowlerjustin29@yahoo.com", "PanCakes2023@)@#")

#access_token = get_access_token(
#    getpass.getpass("Enter your username"),
#    getpass.getpass("Enter your password"),
#)

