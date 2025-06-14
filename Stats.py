import csv from datetime import datetime from collections import defaultdict

CSV_FILE = "host_inventory.csv" HTML_REPORT = "infra_summary_report.html" TEXT_REPORT = "infra_summary_report.txt" EMAIL_RECIPIENT = "admin@example.com"

--- LOAD DATA FROM CSV ---

def load_csv_data(file_path): with open(file_path, newline='') as csvfile: reader = csv.DictReader(csvfile) data = [row for row in reader]

for row in data:
        # Extract and simplify uptime
        if row['Uptime'] and row['Uptime'].endswith('d'):
            row['Uptime'] = row['Uptime'].replace('d', '')

        # Tag environment and region
        hostgroup = row.get('Hostgroup Name', '').lower()
        if 'za' in hostgroup:
            if 'prd' in hostgroup:
                row['Environment'] = 'SA Prod'
                row['Env'] = 'prod'
            elif 'dev' in hostgroup:
                row['Environment'] = 'SA NonProd'
                row['Env'] = 'dev'
            else:
                row['Environment'] = 'SA Other'
                row['Env'] = 'unknown'
        elif 'uk' in hostgroup:
            if 'prd' in hostgroup:
                row['Environment'] = 'UK Prod'
                row['Env'] = 'prod'
            elif 'dev' in hostgroup:
                row['Environment'] = 'UK NonProd'
                row['Env'] = 'dev'
            else:
                row['Environment'] = 'UK Other'
                row['Env'] = 'unknown'
        else:
            row['Environment'] = 'Other'
            row['Env'] = 'unknown'

        # Remove purpose/usage if exists
        row.pop('Purpose/Usage', None)
    return data

--- REPORT CONTENT HOLDERS ---

text_output = [] html_output = ["<html><body><h2>Infrastructure Summary Report</h2>"]

def add_section(title): text_output.append(f"\n--- {title} ---") html_output.append(f"<h3>{title}</h3><ul>")

def add_line(line): text_output.append(line) html_output.append(f"<li>{line}</li>")

def close_section(): html_output.append("</ul>")

--- STATS FUNCTIONS ---

def count_stats(data): add_section("Server Count Summary") total = len(data) prod = len([d for d in data if d['Env'] == 'prod']) nonprod = len([d for d in data if d['Env'] == 'dev']) add_line(f"Total Servers: {total}") add_line(f"Production: {prod}") add_line(f"Non-Production: {nonprod}") close_section()

# UK stats
add_section("UK Server Stats")
uk_data = [d for d in data if 'UK' in d['Environment']]
uk_prod = [d for d in uk_data if d['Env'] == 'prod']
uk_nonprod = [d for d in uk_data if d['Env'] == 'dev']
add_line(f"Total UK Servers: {len(uk_data)}")
add_line(f"Production: {len(uk_prod)}")
for ver in ['RHEL 9', 'RHEL 8', 'RHEL 7']:
    add_line(f"  {ver}: {len([d for d in uk_prod if ver in d['OS Version']])}")
add_line(f"Non-Production: {len(uk_nonprod)}")
for ver in ['RHEL 9', 'RHEL 8', 'RHEL 7']:
    add_line(f"  {ver}: {len([d for d in uk_nonprod if ver in d['OS Version']])}")
hostgroups = defaultdict(int)
for d in uk_data:
    hostgroups[d['Hostgroup Name']] += 1
add_line("Hostgroup counts:")
for k, v in sorted(hostgroups.items(), key=lambda x: x[1], reverse=True):
    add_line(f"  {k}: {v}")
close_section()

# SA stats
add_section("SA Server Stats")
sa_data = [d for d in data if 'SA' in d['Environment']]
sa_prod = [d for d in sa_data if d['Env'] == 'prod']
sa_nonprod = [d for d in sa_data if d['Env'] == 'dev']
add_line(f"Total SA Servers: {len(sa_data)}")
add_line(f"Production: {len(sa_prod)}")
for ver in ['RHEL 9', 'RHEL 8', 'RHEL 7']:
    add_line(f"  {ver}: {len([d for d in sa_prod if ver in d['OS Version']])}")
add_line(f"Non-Production: {len(sa_nonprod)}")
for ver in ['RHEL 9', 'RHEL 8', 'RHEL 7']:
    add_line(f"  {ver}: {len([d for d in sa_nonprod if ver in d['OS Version']])}")
hostgroups = defaultdict(int)
for d in sa_data:
    hostgroups[d['Hostgroup Name']] += 1
add_line("Hostgroup counts:")
for k, v in sorted(hostgroups.items(), key=lambda x: x[1], reverse=True):
    add_line(f"  {k}: {v}")
close_section()

--- UPTIME ANALYSIS ---

def uptime_ranges(data): add_section("Uptime Between 30-90 Days") mid = [d for d in data if d['Uptime'].isdigit() and 30 < int(d['Uptime']) <= 90] add_line(f"Count: {len(mid)}") for d in mid: add_line(f"  {d['Hostname']}: {d['Uptime']} days") close_section()

add_section("Uptime More Than 90 Days")
high = [d for d in data if d['Uptime'].isdigit() and int(d['Uptime']) > 90]
add_line(f"Count: {len(high)}")
for d in high:
    add_line(f"  {d['Hostname']}: {d['Uptime']} days")
close_section()

--- EXPORT REPORTS ---

def save_reports(): with open(TEXT_REPORT, 'w') as txt: txt.write('\n'.join(text_output)) with open(HTML_REPORT, 'w') as html: html.write('\n'.join(html_output) + '</body></html>')

def send_email(): import subprocess with open(HTML_REPORT) as f: html_body = f.read() subprocess.run([ 'mailx', '-a', TEXT_REPORT, '-s', 'Infra Summary Report', '-r', 'noreply@example.com', '-S', 'content-type=text/html', EMAIL_RECIPIENT ], input=html_body.encode())

--- MAIN ---

if name == "main": data = load_csv_data(CSV_FILE) count_stats(data) uptime_ranges(data) save_reports() send_email()

