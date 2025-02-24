"""Snapshot an NXOS System."""

__author__ = "p3rh0ps"
__copyright__ = "Copyright 2024"
__credits__ = ["p3rh0ps"]
__license__ = "MIT"
__version__ = "0.25"
__maintainer__ = "p3rh0ps"
__email__ = "p3rh0ps@gmail.com"
__status__ = "prototype"

from genie.libs.parser.nxos.show_feature import ShowFeature
from genie.libs.parser.nxos.show_platform import ShowVersion, ShowInventory
from genie.libs.parser.nxos.show_environment import ShowEnvironment
from genie.libs.parser.nxos.show_interface import ShowInterfaceStatus, ShowInterface, ShowInterfaceSwitchport, ShowInterfaceTransceiver, ShowIpInterfaceVrfAll, ShowIpv6InterfaceVrfAll
from genie.libs.parser.nxos.show_lag import ShowPortChannelSummary
from genie.libs.parser.nxos.show_vpc import ShowVpc
from genie.libs.parser.nxos.show_ntp import ShowNtpPeerStatus
from genie.libs.parser.nxos.show_spanning_tree import ShowSpanningTreeSummary
from genie.libs.parser.nxos.show_lldp import ShowLldpNeighborsDetail
from genie.libs.parser.nxos.show_routing import ShowRoutingVrfAll
from genie.libs.parser.nxos.show_arp import ShowIpArpDetailVrfAll, ShowIpArpstatisticsVrfAll
from genie.libs.parser.nxos.show_logging import ShowLoggingLogfile
from pyats_genie_command_parse import GenieCommandParse
from genie import testbed

from mods.funcs import (
    banner,
    docs
)

import argparse
import json
from datetime import datetime
from netaddr import valid_ipv6

parser = argparse.ArgumentParser(
                    prog='nxos_parser.py',
                    description='This program takes a snapshot of multiple NXOS system in function of remote\
                        system enabled features with pyats parser.\n It actually supports the following features:\
                            version, inventory, interface stats, ipv4/v6 interfaces, vlan, vpc, ntp, spanning-tree and lldp',
                    epilog='More to come, and you\'re welcome to improve this program by any mean.')

parser.add_argument(
    "-t",
    "--testbed",
    help="testbed file",
    type=str,
    default='testbed.yml',
)

parser.add_argument(
    "-s",
    "--suffix",
    help="suffix used to generate report in results directory",
    type=str,
    default='initial',
)

args = parser.parse_args()

banner()
docs()

NO_ENTRY_FOUND = False

tb = testbed.load(args.testbed)

for tst_dev in tb.devices:

    dev = tb.devices[tst_dev]
    dev.connect(logfile='logs/{}.log'.format(dev.name), log_stdout=False)

    feature_obj = ShowFeature(device=dev)
    parsed_feat_data = feature_obj.parse()
    
    with open('results/{}.{}'.format(dev.name, args.suffix), 'w') as flu:
        version_obj = ShowVersion(device=dev)
        parsed_data = version_obj.parse()

        flu.write("** Clock Information for {}**\n".format(dev.name))
        parsed_data = dev.execute('show clock detail | json-pretty')
        clock_json = json.loads(parsed_data)
        dev_time = datetime.strptime(clock_json['simple_time'], '%H:%M:%S.%f %Z %a %b %d %Y')
        local_time = datetime.now()
        flu.write("Time for {}: {}\n".format(dev.name, dev_time.time()))
        flu.write("Time Source: {}\n".format(clock_json['time_source']))
        flu.write("Time of the local platform {}:\n".format(local_time.time()))
        flu.write("Difference between the 2 timestamps: {}\n".format(local_time - dev_time))
        flu.write("******************************************************\n")

        flu.write("** Version Information **\n")
        flu.write("    Version: {}\n".format(version_obj.parse()['platform']['software']['system_version']))
        flu.write("    Filename: {}\n".format(version_obj.parse()['platform']['software']['system_image_file']))
        flu.write("    Compilation time: {}\n".format(version_obj.parse()['platform']['software']['system_compile_time']))
        flu.write("******************************************************\n")

        parse_obj = GenieCommandParse(nos='nxos')
        parsed_environmt_data = parse_obj.parse_file(show_command='show environment', file_name_and_path='./test_data/{}-environment.txt'.format(dev.name))
        flu.write("** Environment Information **\n")
        for item in parsed_environmt_data['fans']:
            if 'Fan' in item:
                flu.write("** Fan Status **\n")
                flu.write("    Fan Sysname: {}\n".format(item))
                if 'model' in parsed_environmt_data['fans'][item]:
                    flu.write("    Model P/N: {}\n".format(parsed_environmt_data['fans'][item]['model']))
                flu.write("    Hardware Revision: {}\n".format(parsed_environmt_data['fans'][item]['hw']))
                flu.write("    AirFlow Direction: {}\n".format(parsed_environmt_data['fans'][item]['direction']))
                flu.write("    Status: {}\n".format(parsed_environmt_data['fans'][item]['status']))
        flu.write("** Power Information **\n")
        flu.write("** Power Supply **\n")
        for power_id in parsed_environmt_data['power']['power_supply']:
            flu.write("   Power Supply {} Model: {}\n".format(power_id, parsed_environmt_data['power']['power_supply'][power_id]['model']))
            flu.write("   Power Supply {} status: {}\n".format(power_id, parsed_environmt_data['power']['power_supply'][power_id]['status']))
        if 'config_mode' in parsed_environmt_data['power']['power_supply_mode']:
            flu.write("   Power Supply Config Mode: {}\n".format(parsed_environmt_data['power']['power_supply_mode']['config_mode']))         
        if 'oper_mode' in parsed_environmt_data['power']['power_supply_mode']:
            flu.write("   Power Supply Oper Mode: {}\n".format(parsed_environmt_data['power']['power_supply_mode']['oper_mode']))
        flu.write("** Chassis Part Temperature **\n")
        for part in parsed_environmt_data['temperature']['1']:
            flu.write("   {} Current Temperature: {}\n".format(part, parsed_environmt_data['temperature']['1'][part]['current_temp_celsius']))
            flu.write("   {} Status: {}\n".format(part, parsed_environmt_data['temperature']['1'][part]['status']))
        flu.write("******************************************************\n")
        
        inventory_obj = ShowInventory(device=dev)
        parsed_data = inventory_obj.parse()
        flu.write("** Inventory Information **\n")
        flu.write("Chassis \n")
        flu.write("    Description: {}\n".format(parsed_data['name']['Chassis']['description']))
        flu.write("    Pid: {}\n".format(parsed_data['name']['Chassis']['pid']))
        flu.write("    S/N: {}\n".format(parsed_data['name']['Chassis']['serial_number']))
        if 'Slot 1' in parsed_data['name']:
            flu.write("Slot-1 \n")
            flu.write("    Description: {}\n".format(parsed_data['name']['Slot 1']['description']))
            flu.write("    Pid: {}\n".format(parsed_data['name']['Slot 1']['pid']))
            flu.write("    S/N: {}\n".format(parsed_data['name']['Slot 1']['serial_number']))
        if 'Slot 27' in parsed_data['name']:
            flu.write("Slot-27 \n")
            flu.write("    Description: {}\n".format(parsed_data['name']['Slot 27']['description']))
            flu.write("    Pid: {}\n".format(parsed_data['name']['Slot 27']['pid']))
            flu.write("    S/N: {}\n".format(parsed_data['name']['Slot 27']['serial_number']))
            flu.write("******************************************************\n")

        if parsed_feat_data['feature']['vpc']['instance']['1']['state'] == "enabled":
            users_obj = ShowVpc(device=dev)
            parsed_data = users_obj.parse()
            flu.write("** VPC Information *\n")
            flu.write("Domain ID: {}\n".format(parsed_data['vpc_domain_id']))
            flu.write("Role: {}\n".format(parsed_data['vpc_role']))
            flu.write("Peer Status: {}\n".format(parsed_data['vpc_peer_status']))
            flu.write("PKA Status: {}\n".format(parsed_data['vpc_peer_keepalive_status']))
            flu.write("Config Consistency: {}\n".format(parsed_data['vpc_configuration_consistency_status']))
            flu.write("Per Vlan Consistency: {}\n".format(parsed_data['vpc_per_vlan_consistency_status']))
            flu.write("Number of vPC: {}\n".format(parsed_data['num_of_vpcs']))
            flu.write("Peer Gateway Feature: {}\n".format(parsed_data['peer_gateway']))
            flu.write("Dual Active Excluded Vlan list: {}\n".format(parsed_data['dual_active_excluded_vlans']))
            flu.write("Graceful Consistency Check Status: {}\n".format(parsed_data['vpc_graceful_consistency_check_status']))
            flu.write("L3 Peer Router Feature: {}\n".format(parsed_data['operational_l3_peer_router']))
            flu.write("Delay Restore Status: {}\n".format(parsed_data['vpc_delay_restore_status']))
            flu.write("Delay Restore SVI Status: {}\n".format(parsed_data['vpc_role']))
            flu.write("Peer Link Id: {}\n".format(parsed_data['peer_link'][1]['peer_link_id']))
            flu.write("Peer Link Po: {}\n".format(parsed_data['peer_link'][1]['peer_link_ifindex']))
            flu.write("Peer Link Port Status: {}\n".format(parsed_data['peer_link'][1]['peer_link_port_state']))
            flu.write("Peer Link Vlans: {}\n".format(parsed_data['peer_link'][1]['peer_up_vlan_bitset']))
            flu.write("******************************************************\n")
        
        inventory_obj = ShowSpanningTreeSummary(device=dev)
        parsed_data = inventory_obj.parse()
        flu.write("** Spanning-Tree Globally Summarized Information **\n")
        for key in parsed_data['mode']:
            if key == 'rapid-pvst':
                flu.write("{} is in mode: {}\n".format(dev.name, key))
            elif key == 'mst':
                flu.write("{} is in mode: {}\n".format(dev.name, key))
                flu.write("MST Type: {}\n".format(parsed_data['mst_type']))
                flu.write("PVST Simulation Status: {}\n".format(parsed_data['pvst_simulation']))
            else:
                flu.write("{} is in an unknown spanning-tree mode !!!\n".format(dev.name))
        flu.write("Root Bridge For: {}\n".format(parsed_data['root_bridge_for']))
        flu.write("Port Type Default: {}\n".format(parsed_data['port_type_default']))
        flu.write("BPDU Guard Default: {}\n".format(parsed_data['bpdu_guard']))
        flu.write("BPDU Filter Default: {}\n".format(parsed_data['bpdu_filter']))
        flu.write("Bridge Assurance: {}\n".format(parsed_data['bridge_assurance']))
        flu.write("Loop Guard Default: {}\n".format(parsed_data['loop_guard']))
        flu.write("Path Cost Method: {}\n".format(parsed_data['path_cost_method']))
        if parsed_feat_data['feature']['vpc']['instance']['1']['state'] == "enabled":
            flu.write("vPC Peer Switch: {}\n".format(parsed_data['vpc_peer_switch']))
            flu.write("vPC Peer Switch Status: {}\n".format(parsed_data['vpc_peer_switch_status']))
        flu.write("Spanning Tree Lite: {}\n".format(parsed_data['stp_lite']))
        flu.write("** Spanning-Tree Total Statistics **\n")
        flu.write("    Blocking Ports: {}\n".format(parsed_data['total_statistics']['blockings']))
        flu.write("    Listening Ports: {}\n".format(parsed_data['total_statistics']['listenings']))
        flu.write("    Learning Ports: {}\n".format(parsed_data['total_statistics']['learnings']))
        flu.write("    Forwarding Ports: {}\n".format(parsed_data['total_statistics']['forwardings']))
        flu.write("    STP Active Ports: {}\n".format(parsed_data['total_statistics']['stp_actives']))
        flu.write("******************************************************\n")

        flu.write("** NTP Information **\n")
        ntp_obj = ShowNtpPeerStatus(device=dev)
        try:
            parsed_data = ntp_obj.parse()
        except Exception as e:
            if 'Parser Output is empty' in str(e):
                flu.write("No NTP Entry found.\n")
                NO_ENTRY_FOUND = True
                pass
            else:
                flu.write('Unknown error: {}'.format(e))
                exit()

        if not NO_ENTRY_FOUND:
            flu.write("Total Peers Configured: {}\n".format(parsed_data['total_peers']))
            if parsed_data['total_peers'] != 0:
                for ntp_vrf in parsed_data['vrf']:
                    flu.write("NTP VRF {} Configuration:\n".format(ntp_vrf))
                    for peer_ip in parsed_data['vrf'][ntp_vrf]['peer']:
                        flu.write("    Server IP: {}\n".format(parsed_data['vrf'][ntp_vrf]['peer'][peer_ip]['remote']))
                        flu.write("    Server Mode: {}\n".format(parsed_data['vrf'][ntp_vrf]['peer'][peer_ip]['mode']))
                        flu.write("    Server Stratum: {}\n".format(parsed_data['vrf'][ntp_vrf]['peer'][peer_ip]['stratum']))
                        flu.write("    Delay (in second): {}\n".format(parsed_data['vrf'][ntp_vrf]['peer'][peer_ip]['delay']))
                        flu.write("    Reach (number): {}\n".format(parsed_data['vrf'][ntp_vrf]['peer'][peer_ip]['reach']))
        NO_ENTRY_FOUND = False
        flu.write("******************************************************\n")

        intf_gen_obj = ShowInterface(device=dev)
        parsed_data = intf_gen_obj.parse()
        intf_swp_obj = ShowInterfaceSwitchport(device=dev)
        parsed_swp_data = intf_swp_obj.parse()
     
        po_sum_obj = ShowPortChannelSummary(device=dev)
        try:
            parsed_po_sum_data = po_sum_obj.parse()
        except Exception as e:
            if 'Parser Output is empty' in str(e):
                pass
            else:
                flu.write('Unknown error: {}'.format(e))
                exit()
        
        flu.write("** Interfaces Information **\n")
        for intfs in parsed_data:
            flu.write("--------------------------------\n")
            flu.write("Interface Name: {}\n".format(intfs))
            if 'description' in parsed_data[intfs]:
                flu.write("Interface Description: {}\n".format(parsed_data[intfs]['description']))
            if 'types' in parsed_data[intfs]:
                flu.write("Interface Type: {}\n".format(parsed_data[intfs]['types']))
            if 'port_mode' in parsed_data[intfs]:
                flu.write("Interface Mode: {}\n".format(parsed_data[intfs]['port_mode']))
                if parsed_data[intfs]['port_mode'] == 'trunk':
                    flu.write("Interface Trunk vlan(s): {}\n".format(parsed_swp_data[intfs]['trunk_vlans']))
                    flu.write("Interface Native vlan: {}\n".format(parsed_swp_data[intfs]['native_vlan']))
                elif parsed_data[intfs]['port_mode'] == 'access':
                    flu.write("Interface Access vlan {}\n".format(parsed_swp_data[intfs]['access_vlan']))
            if 'port_speed' in parsed_data[intfs]:
                flu.write("Interface Speed: {}{}\n".format(parsed_data[intfs]['port_speed'], parsed_data[intfs]['port_speed_unit']))
            if 'duplex_mode' in parsed_data[intfs]:
                flu.write("Interface Duplex: {}\n".format(parsed_data[intfs]['duplex_mode']))
            if 'mac_address' in parsed_data[intfs]:
                flu.write("Interface Mac-address: {}\n".format(parsed_data[intfs]['mac_address']))
            if 'ipv4' in parsed_data[intfs]:
                for ipv4 in parsed_data[intfs]['ipv4']:
                    flu.write("Interface IPv4: {}\n".format(ipv4))
            if 'port-channel' in intfs and parsed_data[intfs]['port_channel']['port_channel_member'] == True:
                flu.write("Port-Channel Protocol Type: {}\n".format(parsed_po_sum_data['interfaces'][intfs.capitalize()]['protocol']))
                flu.write("Port-Channel Layer: {}\n".format(parsed_po_sum_data['interfaces'][intfs.capitalize()]['layer']))
                flu.write("Port-Channel possess {} interfaces: {}\n".format(len(parsed_data[intfs]['port_channel']['port_channel_member_intfs']), parsed_data[intfs]['port_channel']['port_channel_member_intfs']))
                for mbmr in parsed_data[intfs]['port_channel']['port_channel_member_intfs']:
                    flu.write("Port-Channel Member {} Status Bundle is: {}\n".format(mbmr, parsed_po_sum_data['interfaces'][intfs.capitalize()]['members'][mbmr]['flags']))
            elif 'Ethernet' in intfs and parsed_data[intfs]['port_channel']['port_channel_member'] == True:
                flu.write("Interface is a part of the Port-Channel {}\n".format(parsed_data[intfs]['port_channel']['port_channel_int']))
            else:
                flu.write("This interface is not part of a port-channel\n")
            flu.write("Interface Link State: {}\n".format(parsed_data[intfs]['link_state']))
            flu.write("Interface Oper State: {}\n".format(parsed_data[intfs]['oper_status']))
            if 'admin_state' in parsed_data[intfs]:
                flu.write("Interface Admin State: {}\n".format(parsed_data[intfs]['admin_state']))
            flu.write("Interface MTU: {}\n".format(parsed_data[intfs]['mtu']))
            if 'last_link_flapped' in parsed_data[intfs]:
                flu.write("Interface Last Link Flapped: {}\n".format(parsed_data[intfs]['last_link_flapped']))
            if 'last_clear_counters' in parsed_data[intfs]:
                flu.write("Interface Last Clear Counters: {}\n".format(parsed_data[intfs]['last_clear_counters']))
            if 'counters' in parsed_data[intfs] and 'in_errors' in parsed_data[intfs]['counters']:
                flu.write("####Interface Counters \n")
                flu.write("    in_errors: {}\n".format(parsed_data[intfs]['counters']['in_errors']))
                flu.write("    in_overrun: {}\n".format(parsed_data[intfs]['counters']['in_overrun']))
                flu.write("    in_underrun: {}\n".format(parsed_data[intfs]['counters']['in_underrun']))
                flu.write("    in_bad_etype_drop: {}\n".format(parsed_data[intfs]['counters']['in_bad_etype_drop']))
                flu.write("    in_unknown_protos: {}\n".format(parsed_data[intfs]['counters']['in_unknown_protos']))
                flu.write("    in_if_down_drop: {}\n".format(parsed_data[intfs]['counters']['in_if_down_drop']))
                flu.write("    in_discard: {}\n".format(parsed_data[intfs]['counters']['in_discard']))
                flu.write("    out_errors: {}\n".format(parsed_data[intfs]['counters']['in_errors']))
                flu.write("    out_collision: {}\n".format(parsed_data[intfs]['counters']['out_collision']))
                flu.write("    out_deferred: {}\n".format(parsed_data[intfs]['counters']['out_deferred']))
                flu.write("    out_late_collision: {}\n".format(parsed_data[intfs]['counters']['out_late_collision']))
                flu.write("    out_lost_carrier: {}\n".format(parsed_data[intfs]['counters']['out_lost_carrier']))
                flu.write("    out_no_carrier: {}\n".format(parsed_data[intfs]['counters']['out_no_carrier']))
                flu.write("    out_babble: {}\n".format(parsed_data[intfs]['counters']['out_babble']))
                flu.write("    out_discard: {}\n".format(parsed_data[intfs]['counters']['out_discard']))
                flu.write("    out_mac_pause_frames: {}\n".format(parsed_data[intfs]['counters']['out_mac_pause_frames']))
        flu.write("******************************************************\n")

        intf_transceiver_obj = ShowInterfaceTransceiver(device=dev)
        parsed_data = intf_transceiver_obj.parse()
        flu.write("** Transceivers Information **\n")
        for intfs in parsed_data:
            if 'transceiver_present' in parsed_data[intfs]:
                flu.write("Transceiver Type: {}\n".format(parsed_data[intfs]['transceiver_type']))
                flu.write("Transceiver Name: {}\n".format(parsed_data[intfs]['name']))
                flu.write("Transceiver S/N: {}\n".format(parsed_data[intfs]['serial_number']))
                if 'revision' in parsed_data[intfs]:
                    flu.write("Transceiver Revision: {}\n".format(parsed_data[intfs]['revision']))
                flu.write("Transceiver P/N: {}\n".format(parsed_data[intfs]['part_number']))
                flu.write("Transceiver Vendor OUI: {}\n".format(parsed_data[intfs]['vendor_oui']))
        flu.write("******************************************************\n")

        ipv4_int_obj = ShowIpInterfaceVrfAll(device=dev)
        parsed_data = ipv4_int_obj.parse()
        flu.write("** IPv4 interfaces Information **\n")
        for intfs in parsed_data:
            flu.write("Interface Name: {}\n".format(intfs))
            flu.write("Interface Status: {}\n".format(parsed_data[intfs]['interface_status']))
            flu.write("Assigned VRF: {}\n".format(parsed_data[intfs]['vrf']))
            flu.write("IP Mtu: {}\n".format(parsed_data[intfs]['ip_mtu']))
            for ipv4 in parsed_data[intfs]['ipv4']:
                if 'secondary' in parsed_data[intfs]['ipv4'][ipv4] and parsed_data[intfs]['ipv4'][ipv4]['secondary'] is True:
                    flu.write("    IPv4 Secondary Address: {}\n".format(ipv4))
                else:
                    flu.write("    IPv4 Address: {}\n".format(ipv4))
            flu.write("Proxy Arp Status: {}\n".format(parsed_data[intfs]['proxy_arp']))
            flu.write("Local Proxy Arp Status: {}\n".format(parsed_data[intfs]['local_proxy_arp']))
            flu.write("Multicast Routing Status: {}\n".format(parsed_data[intfs]['multicast_routing']))
            flu.write("ICMP Redirect Status: {}\n".format(parsed_data[intfs]['icmp_redirects']))
            flu.write("Icmp Unreachable Status: {}\n".format(parsed_data[intfs]['icmp_unreachable']))
            flu.write("Icmp Port Unreachable Status: {}\n".format(parsed_data[intfs]['icmp_port_unreachable']))  
            flu.write("Directed Broadcast: {}\n".format(parsed_data[intfs]['directed_broadcast']))
            flu.write("uRPF Status: {}\n".format(parsed_data[intfs]['unicast_reverse_path']))
        flu.write("******************************************************\n")

        ipv6_int_obj = ShowIpv6InterfaceVrfAll(device=dev)
        try:
            parsed_data = ipv6_int_obj.parse()
        except Exception as e:
            if 'Parser Output is empty' in str(e):
                flu.write("No IPv6 Entry found.\n")
                NO_ENTRY_FOUND = True
                pass
            else:
                flu.write('Unknown error: {}'.format(e))
                exit()

        if not NO_ENTRY_FOUND:
            flu.write("** IPv6 interfaces Information **\n")
            for intfs in parsed_data:
                flu.write("Interface Name: {}\n".format(intfs))
                flu.write("Interface Status: {}\n".format(parsed_data[intfs]['interface_status']))
                flu.write("Assigned VRF: {}\n".format(parsed_data[intfs]['vrf']))
                flu.write("Enabled Status: {}\n".format(parsed_data[intfs]['enabled']))
                flu.write("Link Local Address: {}\n".format(parsed_data[intfs]['ipv6']['ipv6_link_local']))
                flu.write("IPv6 Mtu: {}\n".format(parsed_data[intfs]['ipv6']['ipv6_mtu']))
                flu.write("Multicast Group Status: {}\n".format(parsed_data[intfs]['ipv6']['multicast_groups']))
                if parsed_data[intfs]['ipv6']['multicast_groups']:
                    flu.write("Multicast Group: {}\n".format(parsed_data[intfs]['ipv6']['ipv6_multicast_groups']))
                for key in parsed_data[intfs]['ipv6']:
                    if '/' in key and valid_ipv6(key.split('/')[0]):
                        flu.write("Global IPv6 Address\n")
                        flu.write("  IPv6 Address: {}\n".format(key))
                        flu.write("  IPv6 Status: {}\n".format(parsed_data[intfs]['ipv6'][key]['status']))
                flu.write("IPv6 uRPF Status: {}\n".format(parsed_data[intfs]['ipv6']['ipv6_unicast_rev_path_forwarding']))
        NO_ENTRY_FOUND = False
        flu.write("******************************************************\n")

        flu.write("** LLDP Information for {}**\n".format(dev.name))
        lldp_obj = ShowLldpNeighborsDetail(device=dev)
        try:
            parsed_data = lldp_obj.parse()
        except Exception as e:
            if 'Parser Output is empty' in str(e):
                flu.write("No LLDP Entry found.\n")
                NO_ENTRY_FOUND = True
                pass
            else:
                flu.write('Unknown error: {}'.format(e))
                exit()
            
        if not NO_ENTRY_FOUND:
            for local_intf in parsed_data['interfaces']:
                for neigh_intf in parsed_data['interfaces'][local_intf]['port_id']:
                    for neighbor in parsed_data['interfaces'][local_intf]['port_id'][neigh_intf]['neighbors']:
                        flu.write("Local Port: {}\n".format(local_intf))
                        flu.write("Neighbor System Name: {}\n".format(parsed_data['interfaces'][local_intf]['port_id'][neigh_intf]['neighbors'][neighbor]['system_name']))
                        flu.write("Neighbor System Description: {}\n".format(parsed_data['interfaces'][local_intf]['port_id'][neigh_intf]['neighbors'][neighbor]['system_description']))
                        flu.write("Neighbor Port Id: {}\n".format(neigh_intf))
                        flu.write("Neighbor Chassis id: {}\n".format(parsed_data['interfaces'][local_intf]['port_id'][neigh_intf]['neighbors'][neighbor]['chassis_id']))
                        flu.write("Neighbor IPv4 Mgmt: {}\n".format(parsed_data['interfaces'][local_intf]['port_id'][neigh_intf]['neighbors'][neighbor]['management_address_v4']))
                        flu.write("Neighbor IPv6 Mgmt: {}\n".format(parsed_data['interfaces'][local_intf]['port_id'][neigh_intf]['neighbors'][neighbor]['management_address_v6']))
                        flu.write("Vlan_id: {}\n".format(parsed_data['interfaces'][local_intf]['port_id'][neigh_intf]['neighbors'][neighbor]['vlan_id']))
        NO_ENTRY_FOUND = False
        flu.write("******************************************************\n")

        flu.write("** Routing Information for {}**\n".format(dev.name))
        routing_obj = ShowRoutingVrfAll(device=dev)
        parsed_data = routing_obj.parse()

        for vrf in parsed_data['vrf']:
            if vrf == 'default':
                address_family = 'ipv4 unicast'
            else:
                address_family = 'vpnv4 unicast'
            flu.write("** Unicast IPv4 Routing Information for vrf {}**\n".format(vrf))
            
            for prefix in parsed_data['vrf'][vrf]['address_family'][address_family]['ip']:
                flu.write("    Prefix: {}\n".format(prefix))
                if 'attach' in parsed_data['vrf'][vrf]['address_family'][address_family]['ip'][prefix] and parsed_data['vrf'][vrf]['address_family'][address_family]['ip'][prefix]['attach'] == 'attached':
                    flu.write("    Locally Attached Route\n")
                flu.write("    ---> Number of Best Route in RIB: {}\n".format(parsed_data['vrf'][vrf]['address_family'][address_family]['ip'][prefix]['ubest_num']))
                for bst_rt in parsed_data['vrf'][vrf]['address_family'][address_family]['ip'][prefix]['best_route']['unicast']['nexthop']:
                    flu.write("    ---> Best Route: {}\n".format(bst_rt))
                    for proto in parsed_data['vrf'][vrf]['address_family'][address_family]['ip'][prefix]['best_route']['unicast']['nexthop'][bst_rt]['protocol']:
                        flu.write("    ---> Protocol: {}\n".format(proto))
                        if proto == 'direct' or proto == 'local':
                            flu.write("    ---> Directly attached route via: {}\n".format(parsed_data['vrf'][vrf]['address_family'][address_family]['ip'][prefix]['best_route']['unicast']['nexthop'][bst_rt]['protocol'][proto]['interface']))
                        flu.write("    ---> Route Preference: {}\n".format(parsed_data['vrf'][vrf]['address_family'][address_family]['ip'][prefix]['best_route']['unicast']['nexthop'][bst_rt]['protocol'][proto]['preference']))
                        flu.write("    ---> Route Metric: {}\n".format(parsed_data['vrf'][vrf]['address_family'][address_family]['ip'][prefix]['best_route']['unicast']['nexthop'][bst_rt]['protocol'][proto]['metric']))
                        flu.write("    ---> Route Uptime: {}\n".format(parsed_data['vrf'][vrf]['address_family'][address_family]['ip'][prefix]['best_route']['unicast']['nexthop'][bst_rt]['protocol'][proto]['uptime']))               
        flu.write("******************************************************\n")

        flu.write("** Ipv4 Arp Information for {}**\n".format(dev.name))
        parsed_data = dev.execute('show ip arp detail vrf all | json-pretty')
        arp_json = json.loads(parsed_data)
        flu.write("Total Number of ARP Entries: {}\n".format(arp_json['TABLE_vrf']['ROW_vrf']['cnt-total']))
        for arp_id in range(len(arp_json['TABLE_vrf']['ROW_vrf']['TABLE_adj']['ROW_adj'])):
            flu.write("####")
            flu.write("---> ARP Adjacency IP: {}\n".format(arp_json['TABLE_vrf']['ROW_vrf']['TABLE_adj']['ROW_adj'][arp_id]['ip-addr-out']))
            flu.write("---> ARP Adjacency MAC: {}\n".format(arp_json['TABLE_vrf']['ROW_vrf']['TABLE_adj']['ROW_adj'][arp_id]['mac']))
            flu.write("---> ARP Adjacency VRF: {}\n".format(arp_json['TABLE_vrf']['ROW_vrf']['TABLE_adj']['ROW_adj'][arp_id]['adj-vrf-name']))
            flu.write("---> ARP Physical Interface: {}\n".format(arp_json['TABLE_vrf']['ROW_vrf']['TABLE_adj']['ROW_adj'][arp_id]['phy-intf']))
            flu.write("---> ARP Interface Out: {}\n".format(arp_json['TABLE_vrf']['ROW_vrf']['TABLE_adj']['ROW_adj'][arp_id]['intf-out']))
            flu.write("---> Timestamp: {}\n".format(arp_json['TABLE_vrf']['ROW_vrf']['TABLE_adj']['ROW_adj'][arp_id]['time-stamp']))
        flu.write("******************************************************\n")

        flu.write("** Logging Log Information for {}**\n".format(dev.name))
        parsed_data = dev.execute('show logging log | last 100')
        flu.write(parsed_data)
        flu.write("******************************************************\n")

    dev.disconnect()
