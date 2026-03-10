import requests
import json
from dotenv import load_dotenv
import os
import datetime
import csv

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

def get_install_data(loginobj, installid, startdate, type):
    url = f"https://vrmapi.victronenergy.com/v2/installations/{installid}/stats"

    headers = {
        "Content-Type": "application/json",
        "x-authorization": f"Bearer {loginobj["token"]}"
    }
    
    timestamp = int(datetime.datetime.combine(startdate, datetime.datetime.min.time()).timestamp())
    querystring = {"interval":"15mins", "start":str(timestamp), "type": type}

    response = requests.request("GET", url, headers=headers, params=querystring)
    data = response.json()
    return data

def get_ev_summary_data(loginobj, installid):
    url = f"https://vrmapi.victronenergy.com/v2/installations/{installid}/widgets/EvChargerSummary"

    headers = {
        "Content-Type": "application/json",
        "x-authorization": f"Bearer {loginobj["token"]}"
    }

    querystring = {"instance":"0"}
    response = requests.request("GET", url, headers=headers, params=querystring)
    data = response.json()
    return data




def write_to_csv(data,key,offset):
    file = open(f'output/{key}_{offset}.csv', 'w')
    cw = csv.writer(file)
    c = 0

    for emp in data["records"][key]:
        # if c == 0:

        #     # Writing headers of CSV file
        #     h = emp.keys()
        #     cw.writerow(h)
        #     c += 1

        # Writing data of CSV file
        emp[0] = datetime.datetime.fromtimestamp(emp[0]/1000).strftime('%Y-%m-%d %H:%M:%S')
        cw.writerow(emp)

    file.close()


def main():
    print("Hello, VRM!")
    load_dotenv()
    if os.getenv("VRM_LIVEDATA") == "True":
        loginobj = login()
        get_tokens(loginobj)
        installs = get_installs(loginobj)
        stdate = datetime.date.today() 
        stdate -= datetime.timedelta(days=int(os.getenv("VRM_DAYSPAST")))
        data = get_install_data(loginobj, installs["records"][0]["idSite"], stdate, "live_feed")
        consumption_data = get_install_data(loginobj, installs["records"][0]["idSite"], stdate, "consumption")
        evcs_data = get_install_data(loginobj, installs["records"][0]["idSite"], stdate, "evcs")
        # evdata = get_ev_summary_data(loginobj, installs["records"][0]["idSite"])

        # ensure Gc series has a value for every 15‑minute interval; missing
        # slots will be set to zero so that downstream plots/CSV are complete.
        def fill_missing_intervals(series, interval_ms=15 * 60 * 1000):
            if not series:
                return series
            series_sorted = sorted(series, key=lambda x: x[0])
            filled = []
            current = series_sorted[0][0]
            end = series_sorted[-1][0]
            idx = 0
            while current <= end:
                if idx < len(series_sorted) and series_sorted[idx][0] == current:
                    filled.append(series_sorted[idx])
                    idx += 1
                else:
                    filled.append([current, 0])
                current += interval_ms
            return filled

        if "Gc" in consumption_data.get("records", {}):
            consumption_data["records"]["Gc"] = fill_missing_intervals(consumption_data["records"]["Gc"])
        if "Pc" in consumption_data.get("records", {}):
            consumption_data["records"]["Pc"] = fill_missing_intervals(consumption_data["records"]["Pc"])
        if "Bc" in consumption_data.get("records", {}):
            consumption_data["records"]["Bc"] = fill_missing_intervals(consumption_data["records"]["Bc"])
        if "grid_history_from" in data.get("records", {}):
            data["records"]["grid_history_from"] = fill_missing_intervals(data["records"]["grid_history_from"])
        if "evE" in evcs_data.get("records", {}):
            evcs_data["records"]["evE"] = fill_missing_intervals(evcs_data["records"]["evE"])


        print(json.dumps(consumption_data, indent=4))
        print(json.dumps(evcs_data, indent=4))
        # print(json.dumps(evdata, indent=4))
        print(json.dumps(data, indent=4))
        with open("output/output.json", "w") as outfile:
            json.dump(data, outfile, indent=4)
        with open("output/output_consumption.json", "w") as outfile:
            json.dump(consumption_data, outfile, indent=4)
        with open("output/output_evcs.json", "w") as outfile:
            json.dump(evcs_data, outfile, indent=4)
    else:
        with open("output.json", "r") as file:
            data = json.load(file)
            print("Using test data")
    print(json.dumps(data, indent=4))
    write_to_csv(data, "Pdc", stdate.strftime('%Y-%m-%d'))
    write_to_csv(data, "bs", stdate.strftime('%Y-%m-%d'))
    write_to_csv(data, "bv", stdate.strftime('%Y-%m-%d'))
    write_to_csv(data, "total_solar_yield", stdate.strftime('%Y-%m-%d'))
    write_to_csv(data, "total_consumption", stdate.strftime('%Y-%m-%d'))
    write_to_csv(data, "grid_history_from", stdate.strftime('%Y-%m-%d'))
    write_to_csv(evcs_data, "evE", stdate.strftime('%Y-%m-%d'))
    write_to_csv(consumption_data, "Bc", stdate.strftime('%Y-%m-%d'))
    write_to_csv(consumption_data, "Pc", stdate.strftime('%Y-%m-%d'))
    write_to_csv(consumption_data, "Gc", stdate.strftime('%Y-%m-%d'))
            



if __name__ == "__main__":
    main()
