from jinja2 import Environment, FileSystemLoader
from generate_stats import load_hosts, generate_stats
from datetime import datetime
import subprocess

# HTML generation
def render_html(stats):
    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template("template.html")
    return template.render(
        generated_on=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total=stats["total_hosts"],
        envs=stats["env_location"],
        os_versions=stats["os_count"],
        count_30_90=len(stats["uptime_30_90"]),
        count_90_plus=len(stats["uptime_90_plus"])
    )

# Send email using sendmail
def send_email_using_sendmail(html_body, subject, from_addr, to_addr):
    message = f"""\
From: {from_addr}
To: {to_addr}
Subject: {subject}
MIME-Version: 1.0
Content-Type: text/html

{html_body}
"""

    # Use sendmail to send the email
    process = subprocess.Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=subprocess.PIPE)
    process.communicate(message.encode("utf-8"))

# Main
if __name__ == "__main__":
    hosts = load_hosts("hosts.csv")
    stats = generate_stats(hosts)
    html_report = render_html(stats)

    # Save for backup
    with open("report.html", "w") as f:
        f.write(html_report)

    # Send it
    send_email_using_sendmail(
        html_body=html_report,
        subject="Satellite Host Report",
        from_addr="satellite-report@yourdomain.com",
        to_addr="you@example.com"
    )

    print("Report sent using sendmail.")
