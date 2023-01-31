from requests.packages.urllib3.exceptions import InsecureRequestWarning
import requests
import json
from dotenv import load_dotenv
import os


load_dotenv()

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

username = os.getenv('username') 
password = os.getenv('password')
device_addr = os.getenv('device_ip') # MAY USE IP ADDRESS OR FQDN

HEADERS = {"Accept": "application/yang-data+json"}
AUTH = (username, password)  
URL = (f"https://{device_addr}/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet")

response = requests.get( url=URL, auth=AUTH, headers=HEADERS, verify=False)

interfaces = json.loads(response.text)

for interface in interfaces["Cisco-IOS-XE-native:GigabitEthernet"]:
    print("GigabitEthernet "+ interface["name"])
    print(interface["ip"]["address"])
    print("*" * 80)
