# pexpect

## Script Features

  - use sftp package to upload iperf package on bootflash Nexus Devices
  - use pxssh package to connect to Nexus Devices
  - through ssh connection, use pexpect to activate guestshell and install iperf package
  - Script use ncurses and a matrix pad of 2x3 size
  - Present in 6 different pads the installation process and results
  - Use of Multiprocessing to deploy at the same time in each pad
  - Enjoy and you're welcome to improve it if necessary :)
  
## Tested on the following system:

  - Python version: 3.10.5
  - Pip3 version: 22.3.1
  - Python packages: requirements.txt
  - nxos device: n9kv -- nxos 9.3(10)

## NXOS iperf package:

  - You need to download the epel7 iperf package Filename: iperf-2.0.13-1.el7.x86_64.rpm
  - Create a 'epel' directory at script location 'mkdir epel7'
  - Place rpm package in the directory

## Example of output:

<a href="url"><img src="https://github.com/p3rh0ps/Python-Networking/blob/main/pexpect/pexpect_results.png" align="center" height="1000" width="1000" ></a>

## Test on Nexus:
<p>
  <br>root@bastion:~# s n9kv01</br>
  <br>** NETWORK_LAB **</br>
  <br>... output ommited for brevity</br>
  <br>n9kv01# guestshell</br>
  <br><br>[admin@guestshell ~]$ sudo su -</br>
  <br>Last login: Sat Nov 26 08:14:36 UTC 2022 on pts/4</br>
  <br>[root@guestshell ~]# iperf</br>
  <br>Usage: iperf [-s|-c host] [options]</br>
  <br>Try `iperf --help' for more information.</br>
</p>

## Limitations:

  <br>Due to virtual workloads on my lab EVE-NG with docker and vms, and expect language intensively used sometimes...</br>
  <br>This is a showcase example of pexpect script, with ncurses and multiprocessing do not use in production RESTAPI will remains your first friend :)
