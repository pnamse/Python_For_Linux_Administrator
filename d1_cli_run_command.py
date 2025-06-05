#!/usr/bin/python3.9
#Using subprocess module to run Linux system command
import subprocess

def run_df():
    result = subprocess.run(["df","-h"], capture_output=True, text=True)
    print("Disk Usage")
    print(result.stdout)

run_df()
