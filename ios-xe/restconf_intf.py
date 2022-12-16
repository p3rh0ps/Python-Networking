import sys
import requests
import argparse
import logging
from tabulate import tabulate
from getpass import getpass
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
disable_warnings(InsecureRequestWarning)

parser = argparse.ArgumentParser(
        prog = 'restconf_intf.py',
        description = 'Configure interfaces through Restconf and Python',
        epilog = 'Repetition is learning, code, code and code ...!')
parser.add_argument(
        '-H',
        '--host',
        type=str,
        help='FQDN or IPv4 address, default 10.255.255.200',
        default="10.255.255.200")
parser.add_argument(
        '-PR',
        '--restproto',
        type=str,
        help='http or https, for https certs are not verified',
        default="https")
parser.add_argument(
        '-PT',
        '--restport',
        type=str,
        help='TCP PORT Range default 443',
        default="443")
parser.add_argument(
        '-MT',
        '--method',
        type=str,
        help='RESTAPI Method to user on the object: Create "POST" or\
        Change "PUT" or "PATCH"',
        default="POST")
parser.add_argument(
        '-v',
        '--verbose',
        action='store_true')
args = parser.parse_args()

HOST = args.host
REST_PROTO = args.restproto
REST_PORT = args.restport
RESOURCE = "/restconf/data/Cisco-IOS-XE-native:native/interface"
USERNAME = input('Please enter a username:\n')
PASSWORD = getpass('Please enter a password:\n')

if args.verbose:
    logging.basicConfig(level=logging.WARNING, filename='restconf-intf.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

headers = {
    "Content-Type":"application/yang-data+json",
    "Accept":"application/yang-data+json, application/yang-data.errors+json"
}

def get_intf() -> None:
    """ Get all interfaces configured on IOS-XE Router with restconf
    """
    payload = { }
    url = f'{REST_PROTO}://{HOST}:{REST_PORT}{RESOURCE}'
    response = requests.get(url,auth=(USERNAME,PASSWORD), headers=headers, json=payload, verify=False)
    response.raise_for_status()
    intf_typ = ["Interface Type:"]
    intf_num = ["Interface Number:"]
    intf_des = ["Interface Description:"]
    intf_enc = ["Interface Encapsulation:"]
    intf_vrf = ["VRF Forwarding:"]
    intf_pri = ["Primary or Secondary IP:"]
    intf_ip4 = ["IPv4 Address:"]
    intf_mas = ["IPv' Netmask:"]
    for key in response.json()["Cisco-IOS-XE-native:interface"].keys():
        interface = response.json()["Cisco-IOS-XE-native:interface"][key]
        for idx, elem in enumerate(interface):
            intf_typ.append(key)
            intf_num.append(elem['name'])
            if 'description' in elem:
                intf_des.append(elem['description'])
            else:
                intf_des.append("None")
            if 'encapsulation' in elem:
                intf_enc.append(elem['encapsulation']['dot1Q']['vlan-id'])
            else:
                intf_enc.append("None")
            if 'vrf' in elem:
                intf_vrf.append(elem['vrf']['forwarding'])
            else:
                intf_vrf.append("default")
            if 'ip' in elem:
                if 'primary' in elem['ip']['address']:
                    intf_pri.append('Primary')
                    intf_ipv4_type = 'primary'
                if 'secondary' in elem['ip']['address']:
                    intf_pri.append('Secondary')
                    intf_ipv4_type = 'secondary'
                intf_ip4.append(elem['ip']['address'][intf_ipv4_type]['address'])
                intf_mas.append(elem['ip']['address'][intf_ipv4_type]['mask'])
            else:
                intf_pri.append('None')
                intf_ip4.append('None')
                intf_mas.append('None')
    print(tabulate([intf_typ, intf_num, intf_des, intf_enc, intf_vrf, intf_pri, intf_ip4, intf_mas], tablefmt="github", numalign="right"))

def conf_intf(method: str, intf_typ:str,intf_num:str,intf_desc:str,intf_ipv4:str,intf_mask:str) -> int:
    """ Configure an interface on IOS-XE Router with restconf
    """
    payload = {
        intf_typ: [
              {
                "name": intf_num,
                "description": intf_desc,
                "ip": {
                  "address": {
                    "primary": {
                      "address": intf_ipv4,
                      "mask": intf_mask
                    }
                  }
                }
              }
            ]
    }
    if method.upper() == "POST":
        url = f'{REST_PROTO}://{HOST}:{REST_PORT}{RESOURCE}'
    if method.upper() == "PUT" or method.upper() == "PATCH":
        url = f'{REST_PROTO}://{HOST}:{REST_PORT}{RESOURCE}/{intf_typ}={intf_num}'

    response = requests.request(method, url, auth=(USERNAME,PASSWORD), headers=headers, json=payload, verify=False)
    response.raise_for_status()
    return response.status_code


if __name__ == "__main__":
    try:
        print("*"*10,"Snapshot before Changes","*"*10)
        get_intf()
        change_code_result = conf_intf(args.method,'Loopback','1','Test2 Loopback','66.1.2.3','255.255.255.255')
    except Exception as err:
        if str(requests.status_codes.codes.BAD_REQUEST) in str(err):
            print("There is an issue with your request, please review the request: method, payload...")
            sys.exit(-1)
        if str(requests.status_codes.codes.UNAUTHORIZED) in str(err):
            print("Credentials are wrong please retry and take care of caplocks")
            sys.exit(-1)
        if str(requests.status_codes.codes.CONFLICT) in str(err):
            print("Your object already exist, please update it with a PATCH request")
            sys.exit(-1)
        print(str(err))
    print("*"*10,"Snapshot After Changes","*"*10)
    get_intf()
    if change_code_result == 204:
        print("Interface updated via PUT or PATCH request!")
    if change_code_result == 200:
        print("Interface created via POST request!")
