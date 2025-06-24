import requests
import csv
import configparser
from datetime import timedelta

# Load secrets
config = configparser.ConfigParser()
config.read('.secrets')

sat_url = config['redhat_satellite']['url']
sat_user = config['redhat_satellite']['username']
sat_pass = config['redhat_satellite']['password']

session = requests.Session()
session.auth = (sat_user, sat_pass)

headers = {'Content-Type': 'application/json'}

def get_satellite_hosts():
    response = session.get(f'{sat_url}/api/hosts', headers=headers)
    response.raise_for_status()
    return response.json().get('results', [])

def parse_env(hostgroup):
    if '_prd' in hostgroup:
        return 'prod'
    elif '_dev' in hostgroup:
        return 'nonprod'
    return 'Other'

def parse_location(name, hostgroup):
    if 'mum' in name:
        return 'MUM'
    if 'uk-' in name or 'uk-' in hostgroup:
        return 'UK'
    if 'za-' in name or 'za-' in hostgroup:
        return 'SA'
    return 'Other'

def process_hosts_to_csv(hosts, filename):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['hostname', 'ip', 'OS Version', 'hostgroup', 'Env', 'Location', 'Uptime', '60-90days', '90dayAbove']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for host in hosts:
            name = host.get('name')
            if 'virt-who' in name:
                continue
            hostgroup = host.get('hostgroup_name', '')
            env = parse_env(hostgroup)
            loc = parse_location(name, hostgroup)
            uptime_days = int(host.get('uptime_seconds', 0)) // 86400
            writer.writerow({
                'hostname': name,
                'ip': host.get('ip', ''),
                'OS Version': host.get('operatingsystem_name', ''),
                'hostgroup': hostgroup,
                'Env': env,
                'Location': loc,
                'Uptime': uptime_days,
                '60-90days': 60 < uptime_days <= 90,
                '90dayAbove': uptime_days > 90
            })

def create_ansible_inventory(csv_file):
    groups = {'prod_SA': [], 'nonprod_SA': [], 'prod_UK': [], 'nonprod_UK': []}
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = f"{row['Env']}_{row['Location']}"
            if key in groups:
                groups[key].append(row['hostname'])
    
    with open('ansible_inventory_satellite.ini', 'w') as inv:
        for group, hosts in groups.items():
            inv.write(f'[{group}]\n')
            inv.writelines([f"{host}\n" for host in hosts])
            inv.write("\n")

sat_hosts = get_satellite_hosts()
process_hosts_to_csv(sat_hosts, 'hosts.csv')
create_ansible_inventory('hosts.csv')
