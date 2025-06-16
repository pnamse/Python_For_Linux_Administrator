import csv
from collections import Counter, defaultdict
from datetime import datetime

def load_hosts(csv_file):
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        return list(reader)

def generate_stats(hosts):
    stats = {
        "total_hosts": len(hosts),
        "env_location": defaultdict(lambda: defaultdict(int)),
        "os_count": Counter(),
        "grouped_hostgroups": defaultdict(lambda: defaultdict(Counter)),
        "uptime_30_90": [],
        "uptime_90_plus": []
    }

    for h in hosts:
        loc = h.get("Location", "Other")
        env = h.get("Env", "Other")

        stats["env_location"][loc][env] += 1
        stats["os_count"][h.get("OS Version", "Unknown")] += 1

        hostgroup = h.get("hostgroup") or "Unknown"
        stats["grouped_hostgroups"][loc][env][hostgroup] += 1

        uptime = int(h.get("Uptime", 0))
        if 30 < uptime < 90:
            stats["uptime_30_90"].append(h)
        elif uptime >= 90:
            stats["uptime_90_plus"].append(h)

    return stats

def write_text_report(stats, filename="report.txt"):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, "w") as f:
        f.write(f"Satellite Host Statistics Report - {now}\n")
        f.write("="*60 + "\n\n")

        # Overall host count
        f.write("Total Hosts: {}\n\n".format(stats["total_hosts"]))

        # Environment Summary (Only UK and SA)
        f.write("Environment Summary by Location:\n")
        for loc in ["UK", "SA"]:
            envs = stats["env_location"].get(loc, {})
            total = sum(envs.values())
            f.write(f"{loc} Hosts (Total: {total}):\n")
            f.write(f"  - Prod: {envs.get('prod', 0)}\n")
            f.write(f"  - Non Prod: {envs.get('nonprod', 0)}\n")
            f.write(f"  - Other: {envs.get('Other', 0)}\n")
        f.write("\n")

        # OS Version Summary
        f.write("OS Version Counts:\n")
        for os, count in stats["os_count"].items():
            f.write(f"  - {os}: {count}\n")
        f.write("\n")

        # Hostgroup Summary (sorted by Location and Env)
        f.write("Hostgroup Counts by Location and Environment:\n")
        for loc in ["UK", "SA"]:
            if loc not in stats["grouped_hostgroups"]:
                continue
            f.write(f"{loc}:\n")
            for env in ["prod", "nonprod", "Other"]:
                if env not in stats["grouped_hostgroups"][loc]:
                    continue
                f.write(f"  {env}:\n")
                for hg, count in sorted(stats["grouped_hostgroups"][loc][env].items()):
                    f.write(f"    - {hg}: {count}\n")
        f.write("\n")

        # Uptime Stats Summary Only
        f.write("Uptime Summary:\n")
        f.write(f"  - Hosts with >30 and <90 days uptime: {len(stats['uptime_30_90'])}\n")
        f.write(f"  - Hosts with >90 days uptime: {len(stats['uptime_90_plus'])}\n")

def write_uptime_host_list(hosts, filename, label):
    with open(filename, "w") as f:
        f.write(f"{label}:\n")
        f.write("="*60 + "\n")
        for h in hosts:
            f.write(f"{h['hostname']} ({h['Uptime']} days)\n")

if __name__ == "__main__":
    hosts = load_hosts("hosts.csv")
    stats = generate_stats(hosts)

    write_text_report(stats)
    write_uptime_host_list(stats["uptime_30_90"], "uptime_30_90_hosts.txt", "Hosts with >30 and <90 days uptime")
    write_uptime_host_list(stats["uptime_90_plus"], "uptime_90_plus_hosts.txt", "Hosts with >90 days uptime")

    print("✅ Reports generated:")
    print(" - report.txt")
    print(" - uptime_30_90_hosts.txt")
    print(" - uptime_90_plus_hosts.txt")
