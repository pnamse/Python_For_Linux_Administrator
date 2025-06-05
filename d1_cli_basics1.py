#!/usr/bin/python3.9
#Using subprocess and sys module to accept system command as input to script and run it on system.
import sys
import subprocess

def run_command(cmd):
    result = subprocess.run(cmd,shell=True, capture_output=True, text=True)
    print(f"output of `{cmd}`")
    print(result.stdout)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: Python3.6 day1_cli.py 'uptime'")
    else:
        run_command(sys.argv[1])

