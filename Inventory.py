import requests
import csv
import json
from datetime import timedelta

# Read secrets
secrets = {}
with open("secrets.txt") as f:
    for line in f:
        key, value = line.strip().split("=", 1)
        secrets[key] = value

USERNAME = secrets["username"]
PASSWORD = secrets["password"]
SATELLITE_URL = secrets["satellite_url"]

# Satellite API URL
HOSTS_URL = f"{SATELLITE_URL}/api/hosts"

# Set up session
session = requests.Session()
session.auth = (USERNAME, PASSWORD)
session.headers.update({"Content-Type": "application/json"})

# Fetch hosts (handle pagination)
def fetch_all_hosts():
    hosts = []
    page = 1
    per_page = 100
    while True:
        response = session.get(HOSTS_URL, params={"per_page": per_page, "page": page})
        response.raise_for_status()
        data = response.json()
        if not data["results"]:
            break
        hosts.extend(data["results"])
        page += 1
    return hosts

# Filter and format host data
def parse_host_data(hosts):
    parsed = []
    for host in hosts:
        if "virt-who" in host["name"]:
            continue
        hostname = host.get("name", "")
        ip = host.get("ip", "")
        os_version = host.get("operatingsystem_name", "") + " " + str(host.get("operatingsystem_major", ""))
        hostgroup = host.get("hostgroup_name", "")
        uptime_seconds = host.get("uptime_seconds", 0)
        uptime_days = round(uptime_seconds / (24 * 3600))

        # Env filter
        if "_dev" in hostgroup:
            env = "nonprod"
        elif "_prd" in hostgroup:
            env = "prod"
        else:
            env = "Other"

        # Location filter
        if "za-" in hostgroup:
            location = "SA"
        elif "uk-" in hostgroup:
            location = "UK"
        else:
            location = "Other"

        parsed.append({
            "hostname": hostname,
            "ip": ip,
            "OS Version": os_version,
            "hostgroup": hostgroup,
            "Env": env,
            "Location": location,
            "Uptime": uptime_days
        })
    return parsed

# Write to CSV
def write_csv(hosts, filename="hosts.csv"):
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["hostname", "ip", "OS Version", "hostgroup", "Env", "Location", "Uptime"])
        writer.writeheader()
        writer.writerows(hosts)

# Create Ansible inventory files
def write_inventory(hosts):
    inventories = {
        "UK_prod": [],
        "UK_nonprod": [],
        "SA_prod": [],
        "SA_nonprod": [],
    }

    for host in hosts:
        key = f"{host['Location']}_{host['Env']}"
        if key in inventories:
            inventories[key].append(host["hostname"])

    for key, lines in inventories.items():
        filename = f"inventory_{key}.ini"
        with open(filename, "w") as f:
            f.write(f"[{key}]\n")
            for host in lines:
                f.write(f"{host}\n")

# Run
if __name__ == "__main__":
    print("Fetching hosts from Satellite...")
    all_hosts = fetch_all_hosts()
    print(f"Total hosts fetched: {len(all_hosts)}")

    print("Parsing host data...")
    parsed_hosts = parse_host_data(all_hosts)

    print("Writing CSV...")
    write_csv(parsed_hosts)

    print("Creating Ansible inventories...")
    write_inventory(parsed_hosts)

    print("Done.")
