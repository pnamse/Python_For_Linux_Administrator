import requests
import json
import yaml
import csv
from datetime import timedelta

# --- CONFIGURATION ---
SATELLITE_URL = "https://satellite.example.com"
API_USERNAME = "your-username"
PASSWORD_FILE = "secrets.txt"

CSV_FILE = "host_inventory.csv"
YAML_FILE = "host_inventory.yaml"

# --- READ PASSWORD FROM FILE ---
def get_password_from_file(path):
    with open(path, "r") as f:
        return f.readline().strip()

# --- FORMAT UPTIME IN HUMAN-READABLE FORMAT ---
def format_uptime(seconds):
    try:
        td = timedelta(seconds=int(seconds))
        days = td.days
        hours, remainder = divmod(td.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{days}d {hours}h {minutes}m"
    except:
        return "N/A"

# --- FETCH HOST DATA FROM SATELLITE ---
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
        results = data.get("results", [])
        if not results:
            break

        all_hosts.extend(results)
        page += 1

    return all_hosts

# --- PARSE HOST DATA FOR REQUIRED FIELDS ---
def parse_host_data(hosts):
    parsed = []
    for host in hosts:
        hostname = host.get("name", "")
        if "virt-who-esx" in hostname.lower():
            continue  # Skip virtual reporting hosts

        ip = host.get("ip") or host.get("interfaces", [{}])[0].get("ip", "")
        uptime_raw = host.get("uptime_seconds", "")
        uptime_hr = format_uptime(uptime_raw)

        # Fetch purpose from host parameters
        purpose = ""
        params = host.get("parameters", [])
        for p in params:
            if p.get("name") == "purpose_usage":
                purpose = p.get("value")
                break

        item = {
            "Hostname": hostname,
            "IP": ip,
            "OS Version": host.get("operatingsystem_name", ""),
            "Purpose/Usage": purpose,
            "Hostgroup Name": host.get("hostgroup_name", ""),
            "Last Patched": host.get("installed_at", ""),
            "Uptime": uptime_hr,
            "Pending Vulnerabilities": host.get("content_facet_attributes", {}).get("errata_counts", {}).get("security", 0)
        }
        parsed.append(item)
    return parsed

# --- WRITE DATA TO CSV ---
def write_csv(data, filename):
    with open(filename, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

# --- WRITE DATA TO YAML ---
def write_yaml(data, filename):
    with open(filename, "w") as f:
        yaml.dump(data, f, default_flow_style=False)

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    print("🔍 Fetching host data from Satellite...")
    hosts = get_all_hosts()
    print(f"✅ {len(hosts)} total hosts retrieved")

    print("🛠 Filtering and parsing host data...")
    structured_data = parse_host_data(hosts)
    print(f"✅ {len(structured_data)} hosts after filtering")

    print("📄 Writing data to CSV...")
    write_csv(structured_data, CSV_FILE)

    print("📄 Writing data to YAML...")
    write_yaml(structured_data, YAML_FILE)

    print(f"✅ Done! Files created:\n- CSV: {CSV_FILE}\n- YAML: {YAML_FILE}")
