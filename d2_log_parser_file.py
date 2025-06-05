#!/usr/bin/python3.9
#Process Logfile for filter keywords and save it in a file
def parse_and_save(in_file,out_file,keywords):
    with open(in_file,'r') as logfile, open(out_file, 'w') as storefile:
        for line in logfile:
            if any(k in line.lower() for k in keywords):
                storefile.write(line)

keywords = ["error", "fail", "unauthorize", "criticle"]
parse_and_save('/tmp/messages','logparser.out',keywords)
