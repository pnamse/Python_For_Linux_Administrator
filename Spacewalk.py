import csv
import configparser
import xmlrpc.client

# Load secrets
config = configparser.ConfigParser()
config.read('.secrets')

url = config['oracle_spacewalk']['url']
username = config['oracle_spacewalk']['username']
password = config['oracle_spacewalk']['password']

client = xmlrpc.client.ServerProxy(f'{url}/rpc/api')
key = client.auth.login(username, password)

def parse_env(group):
    if '_prd' in group:
        return 'prod'
    elif '_dev' in group:
        return 'nonprod'
    return 'Other'

def process_spacewalk_hosts_to_csv():
    systems = client.system.listUserSystems(key)
    with open('oracle.csv', 'w', newline='') as f:
        fieldnames = ['hostname', 'ip', 'OS Version', 'hostgroup', 'Env', 'Location', 'Uptime', '60-90days', '90dayAbove']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for system in systems:
            if 'virt-who' in system['name']:
                continue
            profile = client.system.getDetails(key, system['id'])
            uptime_days = profile.get('uptime', 0) // 86400
            group = profile.get('group_name', '')
            env = parse_env(group)
            writer.writerow({
                'hostname': profile['name'],
                'ip': profile.get('ip_address', ''),
                'OS Version': profile.get('os_name', ''),
                'hostgroup': group,
                'Env': env,
                'Location': 'SA',
                'Uptime': uptime_days,
                '60-90days': 60 < uptime_days <= 90,
                '90dayAbove': uptime_days > 90
            })

def create_ansible_inventory(csv_file, filename):
    groups = {'prod_SA': [], 'nonprod_SA': [], 'prod_UK': [], 'nonprod_UK': []}
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = f"{row['Env']}_{row['Location']}"
            if key in groups:
                groups[key].append(row['hostname'])
    
    with open(filename, 'w') as inv:
        for group, hosts in groups.items():
            inv.write(f'[{group}]\n')
            inv.writelines([f"{host}\n" for host in hosts])
            inv.write("\n")

def merge_csv():
    with open('hosts.csv') as f1, open('oracle.csv') as f2, open('merged_hosts.csv', 'w', newline='') as outf:
        reader1 = csv.DictReader(f1)
        reader2 = csv.DictReader(f2)
        fieldnames = reader1.fieldnames
        writer = csv.DictWriter(outf, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader1:
            writer.writerow(row)
        for row in reader2:
            writer.writerow(row)

process_spacewalk_hosts_to_csv()
create_ansible_inventory('oracle.csv', 'ansible_inventory_oracle.ini')
merge_csv()
