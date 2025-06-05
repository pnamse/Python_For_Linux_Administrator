#!/usr/bin/python3.9
import subprocess

#Function to accept and run command
def run_command(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

#Collecting Output in variables
disk = run_command(["df","-h"])
uptime = run_command("uptime")
#top = run_command(["top","-b","-n1"])
top5 = run_command(["ps","-eo","pid,ppid,cmd,%mem,%cpu","--sort=-%cpu"])
top5_filtered = "\n".join(top5.strip().split("\n")[:6])

#Writing output to file
with open("sys_summary.txt", "w") as f:
    f.write("---Disk Usage----\n")
    f.write(disk +"\n")

    f.write("---Uptime---\n")
    f.write(uptime + "\n")

    f.write("---Top 5 CPU comsuming Processes---\n")
    f.write(top5_filtered + "\n")

print("Saved to sys_summary.txt")
