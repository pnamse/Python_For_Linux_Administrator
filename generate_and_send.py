import csv
from collections import defaultdict, Counter
from datetime import datetime
import subprocess
import os

def parse_env(hostgroup):
    if '_prd' in hostgroup:
        return 'prod'
    elif '_dev' in hostgroup:
        return 'nonprod'
    else:
        return 'Other'

def parse_location(hostgroup):
    if hostgroup.startswith('uk-'):
        return 'UK'
    elif hostgroup.startswith('za-'):
        return 'SA'
    else:
        return 'Other'

def load_data(csv_file):
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        return list(reader)

def group_by_location_env(hosts):
    env_location = defaultdict(lambda: defaultdict(int))
    os_count = Counter()
    hostgroup_count = defaultdict(int)
    grouped_hostgroups = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    uptime_30_90 = defaultdict(lambda: defaultdict(list))
    uptime_90_plus = defaultdict(lambda: defaultdict(list))

    for host in hosts:
        hostgroup = host.get('hostgroup', 'Unknown') or 'Unknown'
        env = parse_env(hostgroup)
        loc = parse_location(hostgroup)

        env_location[loc][env] += 1
        os_count[host['OS Version']] += 1
        hostgroup_count[hostgroup] += 1
        grouped_hostgroups[loc][env][hostgroup] += 1

        uptime_days = int(float(host['Uptime']))
        host['Uptime'] = str(uptime_days)

        if 30 < uptime_days < 90:
            uptime_30_90[loc][env].append(host)
        elif uptime_days >= 90:
            uptime_90_plus[loc][env].append(host)

    return {
        'total_hosts': len(hosts),
        'env_location': env_location,
        'os_count': os_count,
        'hostgroup_count': hostgroup_count,
        'grouped_hostgroups': grouped_hostgroups,
        'uptime_30_90_grouped': uptime_30_90,
        'uptime_90_plus_grouped': uptime_90_plus
    }

def save_uptime_hosts(grouped_data, filename):
    with open(filename, 'w') as f:
        for loc in grouped_data:
            f.write(f"\n### {loc} ###\n")
            for env in grouped_data[loc]:
                f.write(f"\n--- {env.upper()} ---\n")
                for host in sorted(grouped_data[loc][env], key=lambda x: int(x.get("Uptime", 0)), reverse=True):
                    f.write(f"{host['hostname']} | {host['ip']} | {host['OS Version']} | {host['Uptime']} days\n")

def create_html_report(stats, output_file="report.html"):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
  <title>Satellite Host Statistics</title>
  <style>
    body {{ font-family: Arial, sans-serif; padding: 20px; }}
    h2 {{ color: #2c3e50; }}
    table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
    th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
    th {{ background-color: #f2f2f2; }}
  </style>
</head><body>
  <h2>Satellite Host Statistics Report</h2>
  <p>Generated at: {now}</p>
  <hr>
"""

    html += f"<h3>Total Hosts: {stats['total_hosts']}</h3>"
    html += "<h3>Environment Summary by Location</h3><table><tr><th>Location</th><th>Prod</th><th>Non Prod</th><th>Other</th><th>Total</th></tr>"
    for loc in sorted(stats["env_location"]):
        envs = stats["env_location"][loc]
        total = sum(envs.values())
        html += f"<tr><td>{loc}</td><td>{envs.get('prod', 0)}</td><td>{envs.get('nonprod', 0)}</td><td>{envs.get('Other', 0)}</td><td>{total}</td></tr>"
    html += "</table>"

    html += "<h3>OS Version Summary</h3><table><tr><th>OS Version</th><th>Count</th></tr>"
    for os, count in stats["os_count"].items():
        html += f"<tr><td>{os}</td><td>{count}</td></tr>"
    html += "</table>"

    html += "<h3>Hostgroup Summary</h3>"
    for loc in sorted(stats["grouped_hostgroups"]):
        html += f"<h4>{loc}</h4>"
        for env in sorted(stats["grouped_hostgroups"][loc]):
            html += f"<b>{env}</b><table><tr><th>Hostgroup</th><th>Count</th></tr>"
            for hg, count in sorted(stats["grouped_hostgroups"][loc][env].items()):
                html += f"<tr><td>{hg}</td><td>{count}</td></tr>"
            html += "</table>"

    html += "<h3>Uptime between 30 and 90 days</h3>"
    for loc in sorted(stats['uptime_30_90_grouped']):
        html += f"<h4>{loc}</h4>"
        for env in sorted(stats['uptime_30_90_grouped'][loc]):
            html += f"<b>{env}</b><table><tr><th>Hostname</th><th>IP</th><th>OS</th><th>Uptime (days)</th></tr>"
            for h in sorted(stats['uptime_30_90_grouped'][loc][env], key=lambda x: int(x.get('Uptime', 0)), reverse=True):
                html += f"<tr><td>{h['hostname']}</td><td>{h['ip']}</td><td>{h['OS Version']}</td><td>{h['Uptime']}</td></tr>"
            html += "</table>"

    html += "<h3>Uptime greater than 90 days</h3>"
    for loc in sorted(stats['uptime_90_plus_grouped']):
        html += f"<h4>{loc}</h4>"
        for env in sorted(stats['uptime_90_plus_grouped'][loc]):
            html += f"<b>{env}</b><table><tr><th>Hostname</th><th>IP</th><th>OS</th><th>Uptime (days)</th></tr>"
            for h in sorted(stats['uptime_90_plus_grouped'][loc][env], key=lambda x: int(x.get('Uptime', 0)), reverse=True):
                html += f"<tr><td>{h['hostname']}</td><td>{h['ip']}</td><td>{h['OS Version']}</td><td>{h['Uptime']}</td></tr>"
            html += "</table>"

    html += "</body></html>"
    with open(output_file, "w") as f:
        f.write(html)

def send_email_with_attachments(subject, to_address, text_file, attachments):
    boundary = "===BOUNDARY==="
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    email_headers = f"""Subject: {subject}
To: {to_address}
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="{boundary}"

--{boundary}
Content-Type: text/plain; charset="utf-8"
Content-Disposition: inline

Report generated on {now}

"""

    with open(text_file) as tf:
        email_body = email_headers + tf.read()

    for file in attachments:
        filename = os.path.basename(file)
        with open(file, "rb") as f:
            content = f.read().decode('latin1')  # safely include binary content
        email_body += f"""
--{boundary}
Content-Type: application/octet-stream
Content-Disposition: attachment; filename="{filename}"

{content}
"""
    email_body += f"--{boundary}--\n"

    process = subprocess.Popen(["/usr/sbin/sendmail", "-t"], stdin=subprocess.PIPE)
    process.communicate(email_body.encode("latin1"))

# MAIN EXECUTION
if __name__ == "__main__":
    csv_file = "hosts.csv"
    hosts = load_data(csv_file)
    stats = group_by_location_env(hosts)

    save_uptime_hosts(stats['uptime_30_90_grouped'], "uptime_30_90_hosts.txt")
    save_uptime_hosts(stats['uptime_90_plus_grouped'], "uptime_90_plus_hosts.txt")
    create_html_report(stats, "report.html")

    # You should generate this from logic or write manually before sending
    text_report = "report.txt"

    send_email_with_attachments(
        subject="Satellite Host Report",
        to_address="your@email.com",
        text_file=text_report,
        attachments=["report.html", "uptime_30_90_hosts.txt", "uptime_90_plus_hosts.txt"]
    )

    print("✅ Email sent with inline report.txt and attached HTML & uptime lists.")
