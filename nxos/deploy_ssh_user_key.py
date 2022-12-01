"""
Example of python script to deploy ssh key via NX-API Call on 6 Nexus
with IPv4 management address 10.255.255.14[0-5]
"""

__author__ = "p3rh0ps"
__copyright__ = "Copyright 2022, p3rh0ps"
__credits__ = ["p3rh0ps"]
__license__ = "MIT"
__version__ = "0.90"
__maintainer__ = "p3rh0ps"
__email__ = "p3rh0ps@gmail.com"
__status__ = "prototype"

import getpass
import requests
import json
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
disable_warnings(InsecureRequestWarning)

switchuser='admin'
switchpassword=getpass.getpass(prompt='Password:')
nos = ["10.255.255.14"+str(lastb) for lastb in range(0,6)]

for ip in nos:
    url=f'https://{ip}/ins'
    headers={'content-type':'application/json-rpc'}
    payload=[
            {
                "jsonrpc": "2.0",
                "method": "cli",
                "params": {
                    "cmd": "configure",
                    "version": 1
                },
                "id": 1
            },
            {
                "jsonrpc": "2.0",
                "method": "cli",
                "params": {
                    "cmd": "username admin sshkey ssh-rsa __PLEASE-INSERT-YOUR-SSH-PUB-KEY-FROM_ID.RSA.PUB_HERE__ p3rh0ps@toolbox",
                    "version": 1
                },
                "id": 2
            }
        ]

    response = requests.post(url,data=json.dumps(payload),headers=headers,auth=(switchuser,switchpassword),verify=False)
    print(f'SSH Pub Key Insertion response HTTP code {response.status_code} for NOS nxos with IPV4 {ip}')
