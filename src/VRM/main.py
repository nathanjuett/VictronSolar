import requests
import json
from enum import Enum
from dotenv import load_dotenv
import os
import datetime

class InstallDataType(Enum):
    LIVE_FEED = "live_feed"
    CONSUMPTION = "consumption"
    SOLAR_YIELD = "solar_yield"
    LIVE_FEED_OTHER = "live_feed_other"
    KWH = "kwh"
    EVCS = "evcs"

class Interval(Enum):
    MINS15 = {"apiname": "15mins", "ms": 15 * 60 * 1000}
    HOURS = {"apiname": "hours", "ms": 60 * 60 * 1000}
    HOURS2 = {"apiname": "2hours", "ms": 2 * 60 * 60 * 1000}
    DAYS = {"apiname": "days", "ms": 24 * 60 * 60 * 1000}
    WEEKS = {"apiname": "weeks", "ms": 7 * 24 * 60 * 60 * 1000}
    MONTHS = {"apiname": "months", "ms": 30 * 24 * 60 * 60 * 1000}
    YEARS = {"apiname": "years", "ms": 365 * 24 * 60 * 60 * 1000}

def login():
    """
    Logs in to the VRM API and returns the login object containing the access token and user ID.
    Uses the VRM_USERNAME and VRM_PASSWORD environment variables for authentication.
    """
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
    """
    Gets the list of access tokens for the logged-in user and prints the response.
    """
    url = f"https://vrmapi.victronenergy.com/v2/users/{loginobj["idUser"]}/accesstokens/list"

    headers = {
        "Content-Type": "application/json",
        "x-authorization": f"Bearer {loginobj["token"]}"
    }

    response = requests.request("GET", url, headers=headers)

    print(response.text)

def get_installs(loginobj):
    """
    Gets the list of installations for the logged-in user and returns the response as a JSON object.
    """
    url = f"https://vrmapi.victronenergy.com/v2/users/{loginobj["idUser"]}/installations"

    headers = {
        "Content-Type": "application/json",
        "x-authorization": f"Bearer {loginobj["token"]}"
    }

    response = requests.request("GET", url, headers=headers)
    installs = response.json()
    return installs

def get_install_data(loginobj, installid, startdate, data_type: InstallDataType, interval: Interval = Interval.MINS15, enddate: datetime.datetime = datetime.datetime.now()):
    """
    Gets the installation data for a specific installation ID, start date, data type, and interval.
    If Interval is not provided, it defaults to 15 minutes.
    If enddate is not provided, it defaults to the current date and time.
    """
    if enddate is None:
        enddate = startdate

    url = f"https://vrmapi.victronenergy.com/v2/installations/{installid}/stats"

    headers = {
        "Content-Type": "application/json",
        "x-authorization": f"Bearer {loginobj["token"]}"
    }
    
    timestamp = int(datetime.datetime.combine(startdate, datetime.datetime.min.time()).timestamp())
    endtimestamp = int(enddate.timestamp())
    querystring = {"interval": interval.value["apiname"], "start": str(timestamp), "end": str(endtimestamp), "type": data_type.value}

    response = requests.request("GET", url, headers=headers, params=querystring)
    data = response.json()
    return data

def get_ev_summary_data(loginobj, installid):
    """
    Gets the EV charger summary data for a specific installation ID and returns the response as a JSON object.
    Currently not used.
    """
    url = f"https://vrmapi.victronenergy.com/v2/installations/{installid}/widgets/EvChargerSummary"

    headers = {
        "Content-Type": "application/json",
        "x-authorization": f"Bearer {loginobj["token"]}"
    }

    querystring = {"instance":"0"}
    response = requests.request("GET", url, headers=headers, params=querystring)
    data = response.json()
    return data

def main():
    """
    Main function to execute the VRM API calls and save the data to JSON files in the output folder.
    This is really to test functionality and research the API. 
    The data is saved to JSON files for further analysis.
    """ 

    print("Hello, VRM!")
    load_dotenv()
    
    loginobj = login()
    get_tokens(loginobj)
    installs = get_installs(loginobj)
    stdate = datetime.date.today() 
    stdate -= datetime.timedelta(days=int(os.getenv("VRM_DAYSPAST")))
    data = get_install_data(loginobj, installs["records"][0]["idSite"], stdate, InstallDataType.LIVE_FEED,Interval.MONTHS)
    consumption_data = get_install_data(loginobj, installs["records"][0]["idSite"], stdate, InstallDataType.CONSUMPTION,Interval.MONTHS)
    solar_yield_data = get_install_data(loginobj, installs["records"][0]["idSite"], stdate, InstallDataType.SOLAR_YIELD,Interval.MONTHS)
    battery_stats_data = get_install_data(loginobj, installs["records"][0]["idSite"], stdate, InstallDataType.LIVE_FEED_OTHER,Interval.MONTHS)
    kwh_data = get_install_data(loginobj, installs["records"][0]["idSite"], stdate, InstallDataType.KWH,Interval.MONTHS)
    evcs_data = get_install_data(loginobj, installs["records"][0]["idSite"], stdate, InstallDataType.EVCS,Interval.MONTHS)
    evdata = get_ev_summary_data(loginobj, installs["records"][0]["idSite"])

  
    with open("output/output.json", "w") as outfile:
        json.dump(data, outfile, indent=4)
    with open("output/output_consumption.json", "w") as outfile:
        json.dump(consumption_data, outfile, indent=4)
    with open("output/output_evcs.json", "w") as outfile:
        json.dump(evcs_data, outfile, indent=4)
    with open("output/output_solar_yield.json", "w") as outfile:
        json.dump(solar_yield_data, outfile, indent=4)
    with open("output/output_kwh.json", "w") as outfile:
        json.dump(kwh_data, outfile, indent=4)
    with open("output/evdata.json", "w") as outfile:
        json.dump(evdata, outfile, indent=4)
    with open("output/battery_stats_data.json", "w") as outfile:
        json.dump(battery_stats_data, outfile, indent=4)
        
    print("Data saved to output folder.")
  

if __name__ == "__main__":
    main()
