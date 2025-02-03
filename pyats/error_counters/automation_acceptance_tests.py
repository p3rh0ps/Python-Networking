import json
import logging as log
import re
from pyats import aetest
from pyats.log.utils import banner
from genie.utils.diff import Diff
from tabulate import tabulate
import pandas as pd

# -------------
# AE Test Setup
# -------------

class common_setup(aetest.CommonSetup):

    @aetest.subsection
    def connect_to_devices(self, testbed):
        """Connect to all the devices"""
        testbed.connect()
    
    @aetest.subsection
    def loop_mark(self, testbed):
        aetest.loop.mark(Test_Interfaces, device_name=testbed.devices)


class Test_Interfaces(aetest.Testcase):

    @aetest.test
    def setup(self, testbed, device_name):
        self.device = testbed.devices[device_name]


    @aetest.test
    def get_yang_intf_data(self):
        parsed_nxos_interfaces = self.device.rest.get("/restconf/data/Cisco-NX-OS-device:System/intf-items/phys-items/")
        self.parsed_intf_json = parsed_nxos_interfaces.json()


    @aetest.test
    def test_interface_errors(self):
        max_length = 20
        errors_threshold = 0
        self.failed_interfaces = {}
        table_data = []
        for intf in self.parsed_intf_json['phys-items']['PhysIf-list']:
            counter_discards_in = intf['dbgIfIn-items']['discards']
            counter_discards_out = intf['dbgIfOut-items']['discards']
            counter_errors_in = intf['dbgIfIn-items']['errors']
            counter_errors_out = intf['dbgIfOut-items']['errors']
            counters_discards = int(counter_discards_in) + int(counter_discards_out)
            counters_errors = int(counter_errors_in) + int(counter_errors_out)
            counters = counters_errors + counters_discards
            table_row = []
            table_row.append(self.device.alias)
            table_row.append(intf['id'])
            table_row.append(intf['phys-items']['fcot-items']['description'])
            table_row.append(intf['layer'])
            table_row.append(intf['mtu'])
            table_row.append(intf['phys-items']['adminSt'])
            if intf.get('descr') is not None:
                table_row.append(intf['descr'])
            else:
                table_row.append('No Description')
            if int(counters) > errors_threshold:
                table_row.append(counters)
                table_row.append(counters_discards)
                table_row.append(counters_errors)
                table_row.append('Failed')
                self.failed_interfaces[intf['id']] = counters
                self.interface_name = intf['id']
                self.error_counter = self.failed_interfaces[intf['id']]
            else:
                table_row.append('N/A')
                table_row.append('N/A')
                table_row.append('N/A')
                table_row.append('Passed')
            table_data.append(table_row)
        df = pd.DataFrame(table_data, columns=['Device', 'Intf', 'Transceiver',
            'Layer', 'mtu', 'AdminState',
            'Description', 'SumCounters', 'DiscCounters', 'ErrCounters',
            'TestStatus'])
        df['Description'] = df['Description'].str.slice(0, max_length)
        df.sort_values(by=['AdminState', 'Device', 'Intf'], inplace=True, ascending=[False,True,False])
        log.info(tabulate(df, headers='keys', tablefmt='github', showindex=False))
        if self.failed_interfaces:
            self.failed('Some interfaces have input or output discards')
        else:
            self.passed('No interfaces have input or output discards')


    @aetest.test
    def get_yang_lldp_data(self):
        parsed_nxos_lldp = self.device.rest.get("/restconf/data/Cisco-NX-OS-device:System/lldp-items/inst-items/if-items/")
        self.parsed_lldp_json = parsed_nxos_lldp.json()


    @aetest.test
    def create_file(self):
        with open(f'JSON/{self.device.alias}_LLDP_infos.json', 'w') as f:
            f.write(json.dumps(self.parsed_lldp_json, indent=4, sort_keys=True))
    
"""
    @aetest.test
    def test_get_lldp_neighbors(self):
       for intf in self.parsed_intf_json['if-items']['If-list']:
"""

class CommonCleanup(aetest.CommonCleanup):
    @aetest.subsection
    def disconnect_from_devices(self, testbed):
        testbed.disconnect()
