import csv
from collections import Counter, defaultdict
from datetime import datetime

# Load CSV
def load_hosts(csv_file):
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        return list(reader)

# Count logic
def generate_stats(hosts):
    stats = {
        "total_hosts": len(hosts),
        "env_location": defaultdict(lambda: {"prod": 0, "nonprod": 0}),
        "os_count": Counter(),
        "hostgroup_count": Counter(),
        "uptime_30_90": [],
        "uptime_90_plus": []
    }

    for h in hosts:
        loc = h["Location"]
        env = h["Env"]
        stats["env_location"][loc][env] += 1
        stats["os_count"][h["OS Version"]] += 1
        stats["hostgroup_count"][h["hostgroup"]] += 1

        uptime = int(h["Uptime"])
        if 30 < uptime < 90:
            stats["uptime_30_90"].append(h)
        elif uptime >= 90:
            stats["uptime_90_plus"].append(h)

    return stats

# Write plain text report
def write_text_report(stats, filename="report.txt"):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, "w") as f:
        f.write(f"Satellite Host Statistics Report - {now}\n")
        f.write("="*50 + "\n")
        f.write(f"Total Hosts: {stats['total_hosts']}\n\n")
        
        for loc, envs in stats["env_location"].items():
            f.write(f"{loc} Hosts:\n")
            f.write(f"  - Prod: {envs['prod']}\n")
            f.write(f"  - Non Prod: {envs['nonprod']}\n")

        f.write("\nOS Version Counts:\n")
        for os, count in stats["os_count"].items():
            f.write(f"  - {os}: {count}\n")

        f.write("\nHostgroup Counts:\n")
        for hg, count in stats["hostgroup_count"].items():
            f.write(f"  - {hg}: {count}\n")

        f.write(f"\nUptime >30 & <90 days: {len(stats['uptime_30_90'])} hosts\n")
        for h in stats["uptime_30_90"]:
            f.write(f"  - {h['hostname']} ({h['Uptime']} days)\n")

        f.write(f"\nUptime >90 days: {len(stats['uptime_90_plus'])} hosts\n")
        for h in stats["uptime_90_plus"]:
            f.write(f"  - {h['hostname']} ({h['Uptime']} days)\n")

# Run
if __name__ == "__main__":
    hosts = load_hosts("hosts.csv")
    stats = generate_stats(hosts)
    write_text_report(stats)
    print("Text report generated: report.txt")
