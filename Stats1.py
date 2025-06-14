import requests
import csv
import yaml
import json
from datetime import timedelta

# Load credentials from file (3 lines: URL, username, password)
with open('satellite_credentials.txt') as f:
    url = f.readline().strip()
    username = f.readline().strip()
    password = f.readline().strip()

# Disable SSL warnings if using self-signed certs
requests.packages.urllib3.disable_warnings()

# Fetch host data from Satellite server
response = requests.get(
    f"{url}/api/hosts",
    auth=(username, password),
    headers={"Content-Type": "application/json"},
    verify=False
)
data = response.json().get('results', [])

# Prepare CSV and YAML data
csv_rows = []
yaml_data = {}

for host in data:
    name = host.get("name")
    ip = host.get("ip")
    os = host.get("operatingsystem_name", "")
    release = host.get("operatingsystem_major", "")
    hostgroup = host.get("hostgroup_name", "").lower()
    uptime_sec = int(host.get("facts", {}).get("uptime_seconds", 0))
    
    # ENV based on hostgroup
    env = "PRD" if "prd" in hostgroup else "DEV" if "dev" in hostgroup else "UNKNOWN"

    # Location based on hostgroup
    location = "SA" if hostgroup.startswith("za-") else "UK" if hostgroup.startswith("uk-") else "OTHER"

    # Uptime in days
    uptime_days = uptime_sec // 86400

    # Append to CSV
    csv_rows.append([name, ip, f"{os} {release}", env, location, uptime_days])

    # Append to YAML
    yaml_data[name] = {
        "ip": ip,
        "ENV": env,
        "Location": location,
        "OS": f"{os} {release}"
    }

# Write CSV
with open("hosts_inventory.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["Hostname", "IP", "OS Version", "ENV", "Location", "Uptime Days"])
    writer.writerows(csv_rows)

# Write YAML
with open("hosts_inventory.yaml", "w") as f:
    yaml.dump(yaml_data, f, default_flow_style=False)

print("Files created: hosts_inventory.csv and hosts_inventory.yaml")
