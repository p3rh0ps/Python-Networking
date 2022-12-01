""" Pexpect script demonstration on Cisco NXOS"""

__author__ = "p3rh0ps"
__copyright__ = "Copyright 2022, p3rh0ps"
__credits__ = ["p3rh0ps"]
__license__ = "MIT"
__version__ = "0.90"
__maintainer__ = "p3rh0ps"
__email__ = "p3rh0ps@gmail.com"
__status__ = "prototype"

from time import sleep
from multiprocessing import Process
from pexpect import pxssh
import sys
import re
import pysftp
import curses
import curses.panel

nexus_hosts = {
        "n9kv11": {
            "ipv4":"10.255.255.140"
            },
        "n9kv12": {
            "ipv4":"10.255.255.141"
            },
        "n9kv01": {
            "ipv4":"10.255.255.142"
            },
        "n9kv02": {
            "ipv4":"10.255.255.143"
            },
        "n9kv03" : {
            "ipv4":"10.255.255.144"
            },
        "n9kv04" : {
            "ipv4":"10.255.255.145"
            }
        }

class nexus():

    def __init__(self, name, ipv4, coor_list=None):
        self.name = name
        self.ipv4 = ipv4
        if coor_list is None:
            coor_list = [0,0,0,0]
        else:
            self.y_b = coor_list[0]
            self.x_b = coor_list[1]
            self.y_e = coor_list[2]
            self.x_e = coor_list[3]

    def add_pad(self, rows_thr, cols_mid):
        self.nx_pad = curses.newpad(rows_thr, cols_mid)

    def add_string(self, row_cursor=0, indent=0, pad_msg=None):
        self.nx_pad.addstr(row_cursor, indent, pad_msg)

    def refresh_pad(self):
        self.nx_pad.refresh(0, 0, self.y_b, self.x_b, self.y_e, self.x_e)

    def getch_pad(self):
        self.nx_pad.getch()

    def deploy_guestshell(self):
        try:
            self.add_string(row_cursor=1, indent=0,
                    pad_msg=f"**0** Uploading via SFTP iperf EPEL7 compatible App to {self.name} /bootflash")
            self.refresh_pad()
            with pysftp.Connection(f'{self.name}', username='admin') as sftp:
                with sftp.cd('/bootflash'):
                    sftp.put('epel7/iperf-2.0.13-1.el7.x86_64.rpm')
            self.add_string(row_cursor=2, indent=0,
                    pad_msg=f"**1** Connecting via SSH to {self.name} with {self.ipv4}")
            self.refresh_pad()
            log_file = open(f'{self.name}_pxssh.log', 'wb')
            child = pxssh.pxssh(timeout=5,logfile=log_file,options={
                            "StrictHostKeyChecking": "no",
                            "UserKnownHostsFile": "/dev/null"})
            child.login(f'{self.ipv4}', 'admin', auto_prompt_reset=False)
            child.prompt()
            self.add_string(row_cursor=3, indent=0,
                    pad_msg=f"**2** Destroy running Guestshell")
            self.refresh_pad()
            child.sendline('guestshell destroy')
            child.expect(r'.*\(y\/n\) \[n\]')
            child.sendline("y")
            child.prompt()
            gs_dis_res = child.expect(['Guest shell has already been destroyed', 'Guest shell is currently activating or deactivating'])
            if gs_dis_res == 0:
                self.add_string(row_cursor=4, indent=0,
                        pad_msg=f'**3** GuestShell has already been destroyed on {self.name}')
                self.refresh_pad()
            elif gs_dis_res == 1:
                self.add_string(row_cursor=4, indent=0,
                        pad_msg=f'**3** GuestShell is currently (de)activating on {host}, relaunch the script')
                sys.exit(0)
            else:
                self.add_string(row_cursor=4, indent=0,
                        pad_msg=f'**3** Waiting for GuestShell to be destroyed on {self.name}')
                self.refresh_pad()
                while True:
                    child.sendline('show logging logfile | last 5')
                    child.prompt()
                    if re.search(r'INSTALL_STATE: Successfully destroyed virt', child.before.decode()) == None:
                        sleep(5)
                    else:
                        self.add_string(row_cursor=5, indent=0,
                            pad_msg=f'**3** GuestShell destroyed on {self.name}')
                        self.refresh_pad()
                        break
            child.sendline('guestshell enable')
            child.prompt()
            self.add_string(row_cursor=6, indent=0,
                    pad_msg=f'**4** Activate GuestShell on {self.name}')
            self.refresh_pad()
            while True:
                child.sendline('show guestshell | no-more')
                child.prompt()
                gs_ena_res = child.expect(['Initializing', 'Installing', 'Activating', 'Activated'])
                if gs_ena_res == 0:
                    self.add_string(row_cursor=7, indent=0,
                            pad_msg=">>> Guestshell FSM is 'Initializing' First Stage...")
                    self.refresh_pad()
                    sleep(30)
                if gs_ena_res == 1:
                    self.add_string(row_cursor=8, indent=0,
                            pad_msg=">>> Guestshell FSM is 'Installing' Second Stage...")
                    self.refresh_pad()
                    sleep(30)
                if gs_ena_res == 2:
                    self.add_string(row_cursor=9, indent=0,
                            pad_msg=">>> Guestshell FSM is 'Activating' (Before-Last)...")
                    self.refresh_pad()
                    sleep(30)
                if  gs_ena_res == 3:
                    self.add_string(row_cursor=10, indent=0,
                            pad_msg=">>> Guestshell is Activated continue script")
                    self.refresh_pad()
                    break
            child.prompt()
            self.add_string(row_cursor=11, indent=0,
                    pad_msg=f"**5** Entering Guestshell")
            self.refresh_pad()
            child.sendline('guestshell')
            child.prompt()
            self.add_string(row_cursor=12, indent=0,
                    pad_msg=f"**6** Elevate to root privilege to install App")
            self.refresh_pad()
            child.sendline('sudo su -')
            child.prompt()
            self.add_string(row_cursor=13, indent=0,
                    pad_msg=f"**7** Install iPerf previously uploaded via sftp on {self.name}")
            self.refresh_pad()
            child.sendline('yum install -y /bootflash/iperf-2.0.13-1.el7.x86_64.rpm')
            child.expect(r'^.*Complete!.*$')
            child.sendline('exit')
            child.prompt()
            child.sendline('exit')
            child.prompt()
            child.logout()
            self.add_string(row_cursor=14, indent=0,
                    pad_msg=f"**8** Guestshell and iPerf operational on {self.name}")
            self.refresh_pad()
            log_file.close()
        except pxssh.ExceptionPxssh as e:
            self.add_string(row_cursor=15, indent=0,
                    pad_msg=f"pxssh failed on login for {self.name}.")
            self.refresh_pad()
            log_file.close()
            print(e)
        except:
            self.add_string(row_cursor=15, indent=0,
                    pad_msg=f"Failed to finish execution of iperf installation on {self.name}.")
            log_file.close()

def draw_pads(stdscr):
    k = 0
    stdscr.keypad(True)
    stdscr.clear()
    stdscr.refresh()
    while (k != ord('q')):
        rows_tot, cols_tot = stdscr.getmaxyx()
        cols_mid = int(0.5*cols_tot)
        rows_thr = int(0.33*rows_tot)
        nexus_pads = []
        counter = 0
        coor = [
                [0, 0, rows_thr, cols_mid],
                [0, cols_mid, rows_thr, cols_tot],
                [rows_thr, 0, 2*rows_thr, cols_mid],
                [rows_thr, cols_mid, 2*rows_thr, cols_tot],
                [2*rows_thr, 0, 3*rows_thr, cols_tot],
                [2*rows_thr, cols_mid, 3*rows_thr, cols_tot]
                ]
        for key, value in nexus_hosts.items():
            nexus_pads.append(nexus(key, value['ipv4'],
                    coor[counter].copy()))
            nexus_pads[counter].add_pad(rows_thr, cols_mid)
            counter+=1

        process_exec = []

        for i in range(0, len(nexus_pads)):
            nexus_pads[i].add_string(row_cursor=0, indent=0,
                    pad_msg=f'*** {nexus_pads[i].name} ***')
            nexus_pads[i].refresh_pad()
            process_exec.insert(i, Process(target=nexus_pads[i].deploy_guestshell))
            process_exec[i].start()

        k = stdscr.getch()

def main():
    curses.wrapper(draw_pads)


if __name__ == "__main__":
    main()
