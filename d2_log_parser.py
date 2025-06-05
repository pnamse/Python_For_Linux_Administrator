#!/usr/bin/python3.9
#Pass logfile to function and filter the keywords
def parse_log(file_path, keywords):
    with open(file_path,'r') as logfile:
        for line in logfile:
            if any(keyword in line.lower() for keyword in keywords):
                print(line.strip())

keywords =['error', 'fail', 'criticle', 'unauthorized']
parse_log('/tmp/messages', keywords)
