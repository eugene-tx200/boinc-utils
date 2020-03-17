#!/usr/bin/env python3
import argparse
from request import Request


host = 'localhost'
port = 31416
# Password stored in /etc/boinc-client/gui_rpc_auth.cfg
password = 'G3d2H5z1M7'

def print_child(et):
    """Print key: value from xml.etree.ElementTree."""
    for child in et:
        print('{}: {}'.format(child.tag, child.text))
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
                    metavar=('URL', 'name', 'password'))
args = parser.parse_args()

if args.get_host_info:
    req = Request(host, port)
    print_child(req.get_host_info())

if args.client_version:
    req = Request(host, port)
    print_child(req.exchange_versions())

if args.get_state:
    req = Request(host, port)
    print_child(req.get_state())

if args.acct_mgr_info:
    req = Request(host, port, password)
    print_child(req.acct_mgr_info())

if args.acct_mgr_attach:
    req = Request(host, port, password)
    url, name, password = args.acct_mgr_attach
    print_child(req.acct_mgr_attach(url, name, password))
