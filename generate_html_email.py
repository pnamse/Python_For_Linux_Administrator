# generate_html_email.py
import json
from datetime import datetime
import subprocess

def load_stats(json_file):
    with open(json_file) as f:
        return json.load(f)

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
    return html

def send_inline_email(subject, to_address, html_body):
    email_msg = f"""Subject: {subject}
MIME-Version: 1.0
Content-Type: text/html
To: {to_address}

{html_body}"""
    process = subprocess.Popen(["/usr/sbin/sendmail", "-t", to_address], stdin=subprocess.PIPE)
    process.communicate(email_msg.encode())

if __name__ == "__main__":
    stats = load_stats("stats.json")
    html_report = create_html_report(stats)
    send_inline_email("Satellite Host Report", "your@email.com", html_report)
    print("✅ Email sent with HTML report.")
