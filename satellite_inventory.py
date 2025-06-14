import requests
import csv
import yaml
import json
from datetime import datetime

# Load credentials from txt file
with open('satellite_credentials.txt') as cred_file:
    lines = cred_file.read().strip().splitlines()
    satellite_url = lines[0].strip()
    username = lines[1].strip()
    password = lines[2].strip()

# Set headers
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# Get host data from Satellite API
response = requests.get(f"{satellite_url}/api/hosts", auth=(username, password), headers=headers, verify=False)
hosts_data = response.json().get('results', [])

# Prepare CSV and YAML output
csv_rows = []
yaml_output = {}

for host in hosts_data:
    name = host.get('name')
    ip = host.get('ip')
    os = host.get('operatingsystem_name', '')
    release = host.get('operatingsystem_major', '')
    hostgroup = host.get('hostgroup_name', '').lower()
    uptime_seconds = host.get('facts', {}).get('uptime_seconds', 0)

    # Determine environment and location
    if 'prd' in hostgroup:
        env = 'PRD'
    elif 'dev' in hostgroup:
        env = 'DEV'
    else:
        env = 'UNKNOWN'

    if 'za-' in hostgroup:
        location = 'SA'
    elif 'uk-' in hostgroup:
        location = 'UK'
    else:
        location = 'OTHER'

    # Uptime in days
    uptime_days = int(uptime_seconds) // 86400 if uptime_seconds else 0

    # Append to CSV
    csv_rows.append([name, ip, os, release, env, location, uptime_days])

    # Append to YAML
    yaml_output[name] = {
        'ip': ip,
        'ENV': env,
        'Location': location,
        'OS': f"{os} {release}"
    }

# Write to CSV
with open('hosts_inventory.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Hostname', 'IP', 'OS', 'Release', 'ENV', 'Location', 'Uptime (Days)'])
    writer.writerows(csv_rows)

# Write to YAML
with open('hosts_inventory.yaml', 'w') as yamlfile:
    yaml.dump(yaml_output, yamlfile, default_flow_style=False)

print("Inventory exported to hosts_inventory.csv and hosts_inventory.yaml")
