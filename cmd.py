#!/usr/bin/env python3
import argparse
import socket
import xml.etree.ElementTree as ET
from request import Request


HOST = 'localhost'
PORT = 31416
# Password stored in /etc/boinc-client/gui_rpc_auth.cfg
PASSWORD = 'G3d2H5z1M7'

def print_child(data):
    for child in data:
        print ('{}: {}'.format(child.tag, child.text))
        if child:
            print_child(child)


parser = argparse.ArgumentParser(allow_abbrev=False)
parser.add_argument('--get_host_info', help='show host info',
                    action='store_true')
parser.add_argument('--client_version', help='show client version',
                    action='store_true')
parser.add_argument('--get_state', help='show entire state',
                    action='store_true')
parser.add_argument('--acct_mgr_info', help='show current account manager info',
                    action='store_true')
parser.add_argument('--acct_mgr_attach', nargs=3, help='attach to account manager',
                    metavar=('URL','name', 'password'))
args = parser.parse_args()

if args.get_host_info:
    r = Request(HOST, PORT)
# Using 'connect()' and 'close()' methods
#    r.connect()
#    data = r.get_host_info()
#    print_child(data)
#    r.close()
# Using 'with'statement
    with r:
        data = r.get_host_info()
        print_child(data)

if args.client_version:
    r = Request(HOST, PORT)
    with r:
        data = r.exchange_versions()
        print_child(data)

if args.get_state:
    r = Request(HOST, PORT)
    with r:
        data = r.get_state()
        print_child(data)

if args.acct_mgr_info:
    r = Request(HOST, PORT, PASSWORD)
    with r:
        data = r.acct_mgr_info()
        print_child(data)

if args.acct_mgr_attach:
    print(args.acct_mgr_attach)
