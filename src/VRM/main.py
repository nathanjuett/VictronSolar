import requests
import json
from dotenv import load_dotenv
import os
import datetime

def login():
    loginurl = "https://vrmapi.victronenergy.com/v2/auth/login"
   
    payload = {
        "username": os.getenv("VRM_USERNAME"),
        "password": os.getenv("VRM_PASSWORD")
    }

    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", loginurl, json=payload, headers=headers)
    print(response.status_code)
    return response.json()
   

def get_tokens(loginobj):
    url = f"https://vrmapi.victronenergy.com/v2/users/{loginobj["idUser"]}/accesstokens/list"

    headers = {
        "Content-Type": "application/json",
        "x-authorization": f"Bearer {loginobj["token"]}"
    }

    response = requests.request("GET", url, headers=headers)

    print(response.text)

def get_installs(loginobj):
    url = f"https://vrmapi.victronenergy.com/v2/users/{loginobj["idUser"]}/installations"

    headers = {
        "Content-Type": "application/json",
        "x-authorization": f"Bearer {loginobj["token"]}"
    }

    response = requests.request("GET", url, headers=headers)
    installs = response.json()
    return installs

def get_install_data(loginobj, installid):
    url = f"https://vrmapi.victronenergy.com/v2/installations/{installid}/stats"

    headers = {
        "Content-Type": "application/json",
        "x-authorization": f"Bearer {loginobj["token"]}"
    }
    stdate = datetime.date.today() 
    stdate -= datetime.timedelta(days=31)
    timestamp = int(datetime.datetime.combine(stdate, datetime.datetime.min.time()).timestamp())
    querystring = {"interval":"15mins", "start":str(timestamp)}

    response = requests.request("GET", url, headers=headers, params=querystring)
    data = response.json()
    return data

def main():
    print("Hello, VRM!")
    load_dotenv()
    if os.getenv("VRM_LIVEDATA") == "True":
        loginobj = login()
        get_tokens(loginobj)
        installs = get_installs(loginobj)
        data = get_install_data(loginobj, installs["records"][0]["idSite"])
        print(json.dumps(data, indent=4))
        with open("output.json", "w") as outfile:
            json.dump(data, outfile, indent=4)
    else:
        print("Using test data")


if __name__ == "__main__":
    main()
