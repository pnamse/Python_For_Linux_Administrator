import requests
import json
import yaml
import csv
import os
from datetime import timedelta

# --- CONFIGURATION ---
SATELLITE_URL = "https://satellite.example.com"
API_USERNAME = "your-username"
PASSWORD_FILE = "secrets.txt"

CSV_FILE = "host_inventory.csv"
YAML_FILE = "host_inventory.yaml"

# --- READ PASSWORD ---
def get_password_from_file(path):
    with open(path, "r") as f:
        return f.readline().strip()

# --- CONVERT SECONDS TO HUMAN READABLE FORMAT ---
def format_uptime(seconds):
    try:
        td = timedelta(seconds=int(seconds))
        days = td.days
        hours, remainder = divmod(td.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{days}d {hours}h {minutes}m"
    except:
        return "N/A"

# --- FETCH HOST DATA ---
def get_all_hosts():
    password = get_password_from_file(PASSWORD_FILE)

    url = f"{SATELLITE_URL}/api/hosts"
    headers = {"Content-Type": "application/json"}
    auth = (API_USERNAME, password)

    all_hosts = []
    page = 1

    while True:
        response = requests.get(url, auth=auth, headers=headers, params={"per_page": 100, "page": page})
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            break

        data = response.json()
        if not data.get("results"):
            break

        all_hosts.extend(data["results"])
        page += 1

    return all_hosts

# --- PARSE & STRUCTURE DATA ---
def parse_host_data(hosts):
    parsed = []
    for host in hosts:
        ip = host.get("ip") or host.get("interfaces", [{}])[0].get("ip", "")
        uptime_raw = host.get("uptime_seconds", "")
        uptime_hr = format_uptime(uptime_raw)

        item = {
            "Hostname": host.get("name", ""),
            "IP": ip,
            "OS Version": host.get("operatingsystem_name", ""),
            "Environment": host.get("environment_name", ""),
            "Last Patched": host.get("installed_at", ""),  # Adjust as needed
            "Uptime": uptime_hr,
            "Pending Vulnerabilities": host.get("content_facet_attributes", {}).get("errata_counts", {}).get("security", 0)
        }
        parsed.append(item)
    return parsed

# --- WRITE TO CSV ---
def write_csv(data, filename):
    with open(filename, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

# --- WRITE TO YAML ---
def write_yaml(data, filename):
    with open(filename, "w") as f:
        yaml.dump(data, f, default_flow_style=False)

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    print("🔍 Fetching host data...")
    hosts = get_all_hosts()
    print(f"✅ {len(hosts)} hosts fetched")

    print("🛠 Parsing host data...")
    structured_data = parse_host_data(hosts)

    print("📄 Writing CSV...")
    write_csv(structured_data, CSV_FILE)

    print("📄 Writing YAML...")
    write_yaml(structured_data, YAML_FILE)

    print(f"✅ Done! CSV: {CSV_FILE}, YAML: {YAML_FILE}")
