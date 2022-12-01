"""
Check device netconf capabilities (YANG models)
"""

__author__ = "p3rh0ps"
__copyright__ = "Copyright 2022, p3rh0ps"
__credits__ = ["p3rh0ps"]
__license__ = "MIT"
__version__ = "0.90"
__maintainer__ = "p3rh0ps"
__email__ = "p3rh0ps@gmail.com"
__status__ = "prototype"

from ncclient import manager
from getpass import getpass

switch_name=input('Please provide Netconf device via FQDN or IP Address:')
netconf_port=input('Please provide Netconf port to use to establish connection:')
switch_user=input('Username:')
switch_password=getpass(prompt='Password:')

conn = manager.connect(
    host=switch_name,
    port=netconf_port,
    username=switch_user,
    password=switch_password,
    hostkey_verify=False,
    device_params={'name': 'nexus'},
    look_for_keys=False
)

for value in conn.server_capabilities:
    print(value)

conn.close_session()
