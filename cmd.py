#!/usr/bin/env python3
import argparse
import sys
import xml.etree.ElementTree as ET
from request import Request, RequestValueError

def print_child(et):
    """Print key: value from xml.etree.ElementTree."""
    if not isinstance(et, ET.Element):
        sys.exit('Error: Reply is not an ET object')
    for child in et:
        print('{}: {}'.format(child.tag, child.text))
        if child:
            print_child(child)

def get_password():
    """Function that read config file(s) and return password or None."""
    path = '/etc/boinc-client/gui_rpc_auth.cfg'
    try:
        with open(path) as file:
            return file.read().strip()
    except FileNotFoundError:
        print('Warning: No such file or directory:', path)
    except PermissionError:
        print('Warning: Permission denied:', path)
    return False

parser = argparse.ArgumentParser(allow_abbrev=False)
parser.add_argument('--host', metavar='hostname[:port]',
                    help='connect to hostname')
parser.add_argument('--passwd', metavar='password',
                    help='password for RPC authentication')
parser.add_argument('--get_host_info', help='show host info',
                    action='store_true')
parser.add_argument('--client_version', help='show client version',
                    action='store_true')
parser.add_argument('--get_state', help='show entire state',
                    action='store_true')
parser.add_argument('--acct_mgr_info', help='show current account manager info',
                    action='store_true')
parser.add_argument('--get_project_status',
                    help='show status of all attached projects',
                    action='store_true')
parser.add_argument('--acct_mgr_attach', nargs=3,
                    help='attach to account manager',
                    metavar=('URL', 'name', 'password'))
parser.add_argument('--lookup_account', nargs=3,
                    help='look for an account in a given project '
                    'and return auth string',
                    metavar=('URL', 'email', 'passwd'))

if __name__ == '__main__':
    args = parser.parse_args()
    host = 'localhost'
    port = 31416
    if args.host:
        host_port = args.host.partition(':')    # ('host', ':', 'port')
        host = host_port[0]
        if host_port[2].isdigit():
            port = host_port[2]
    if args.passwd:
        password = args.passwd
    else:
        password = get_password()
    # Try for Reqest common exceptions
    try:
        if args.get_host_info:
            req = Request(host, port, password)
            print_child(req.simple_request('get_host_info'))
        if args.client_version:
            req = Request(host, port, password)
            print_child(req.simple_request('exchange_versions'))
        if args.get_state:
            req = Request(host, port, password)
            print_child(req.simple_request('get_state'))
        if args.acct_mgr_info:
            req = Request(host, port, password)
            print_child(req.simple_request('acct_mgr_info'))
        if args.get_project_status:
            req = Request(host, port, password)
            print_child(req.simple_request('get_project_init_status'))
        if args.acct_mgr_attach:
            url, name, input_pwd = args.acct_mgr_attach
            req = Request(host, port, password)
            print_child(req.acct_mgr_attach(url, name, input_pwd))
        if args.lookup_account:
            url, email, input_pwd = args.lookup_account
            req = Request(host, port, password)
            auth_key = req.lookup_account(url, email, input_pwd)
            print ('Authenticator: ', auth_key)
    # Catch Request common exceptions
    except OSError as e:
        sys.exit('Error: ' + str(e))
    except TimeoutError:
        sys.exit('Error: Connection timed out')
    except ConnectionRefusedError:
        sys.exit('Error: Connection refused')
    except RequestValueError as e:
        sys.exit('Error: ' + str(e))
