#!/usr/bin/python3.9
#Lets learn how to read yaml file.
#Create infra_inventory.yml file as 
#servers:
#    - name: web-01
#      role: web
#      env: prod
#      region: us-west
#      ip: 10.1.1.10
#    - name: app-01
#      role: app
#      env: prod
#      region: us-east
#      ip: 10.1.2.10
#    - name: db-01
#      role: DB
#      env: prod
#      region: us-west
#      ip: 10.1.1.20

import yaml
import json

with open("infra_inventory.yml", "r") as f:
    data = yaml.safe_load(f)

for server in data["servers"]:
    print(f"{server['name']}({server['role']}) - {server['env']} @ {server['region']} -> {server['ip']}")

#Filter for prod environment
prod_servers = [s for s in data["servers"] if s["env"] == "prod" ]
print("\nProd Servers: ")

for s in prod_servers:
    print(f"{s['name']} - {s['ip']}")

#save the out put to json file yaml to json conversion
with open("prod_servers.json","w") as out:
    json.dump(prod_servers,out,indent=2)
