import requests
import csv
import yaml

# Load credentials from file
with open('satellite_credentials.txt') as f:
    url = f.readline().strip()
    username = f.readline().strip()
    password = f.readline().strip()

# Prepare request headers
headers = {"Content-Type": "application/json"}
requests.packages.urllib3.disable_warnings()

# Function to fetch all hosts with pagination
def fetch_all_hosts():
    page = 1
    per_page = 100
    all_hosts = []

    while True:
        response = requests.get(
            f"{url}/api/hosts",
            auth=(username, password),
            headers=headers,
            params={"page": page, "per_page": per_page},
            verify=False
        )
        if response.status_code != 200:
            print(f"Failed to fetch page {page}: {response.status_code}")
            break

        data = response.json().get("results", [])
        if not data:
            break

        all_hosts.extend(data)
        page += 1

    return all_hosts

# Fetch hosts
hosts_data = fetch_all_hosts()

# Prepare CSV and YAML data
csv_rows = []
yaml_data = {}

for host in hosts_data:
    name = host.get("name")
    if "virt-who" in name.lower():
        continue

    ip = host.get("ip")
    os = host.get("operatingsystem_name", "")
    release = host.get("operatingsystem_major", "")
    hostgroup = host.get("hostgroup_name", "").lower()
    uptime_sec = int(host.get("facts", {}).get("uptime_seconds", 0))

    # ENV and Location
    env = "PRD" if "prd" in hostgroup else "DEV" if "dev" in hostgroup else "UNKNOWN"
    location = "SA" if hostgroup.startswith("za-") else "UK" if hostgroup.startswith("uk-") else "OTHER"
    uptime_days = uptime_sec // 86400

    # Add to CSV
    csv_rows.append([name, ip, f"{os} {release}", env, location, uptime_days])

    # Add to YAML
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

print(f"✅ Fetched {len(csv_rows)} hosts (excluding virt-who). Files written: hosts_inventory.csv and hosts_inventory.yaml")
