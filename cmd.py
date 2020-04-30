#!/usr/bin/env python3
"""Utility to control boinc-client. Copycat of the boinccmd"""
import argparse
import sys
import xml.etree.ElementTree as ET
from request import Request, RequestValueError


DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 31416

def print_child(el_tree):
    """Print key: value from xml.etree.ElementTree."""
    if not isinstance(el_tree, ET.Element):
        sys.exit('Error: Reply is not an ET object')
    for element in el_tree:
        print('{}: {}'.format(element.tag, element.text))
        if element:
            print_child(element)

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

def main():
    """ Main Function. Intended to run from command line"""
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument('--host', metavar='hostname[:port]',
                        help='connect to hostname')
    parser.add_argument('--passwd', metavar='password',
                        help='password for RPC authentication')
    parser.add_argument('--get_host_info', action='store_true',
                        help='show host info')
    parser.add_argument('--client_version', action='store_true',
                        help='show client version')
    parser.add_argument('--get_state', action='store_true',
                        help='show entire state')
    parser.add_argument('--acct_mgr_info', action='store_true',
                        help='show current account manager info')
    parser.add_argument('--get_project_status', action='store_true',
                        help='show status of all attached projects')
    parser.add_argument('--acct_mgr_attach', nargs=3,
                        metavar=('URL', 'name', 'password'),
                        help='attach to account manager')
    parser.add_argument('--lookup_account', nargs=3,
                        metavar=('URL', 'email', 'passwd'),
                        help='look for an account in a given project '
                        'and return auth string')
    parser.add_argument('--project_attach', nargs=2, metavar=('URL', 'auth'),
                        help='attach to project')

    args = parser.parse_args()
    host = DEFAULT_HOST
    port = DEFAULT_PORT
    if args.host:
        host_port = args.host.partition(':')    # ('host', ':', 'port')
        host = host_port[0]
        if host_port[2].isdigit():
            port = host_port[2]
    if args.passwd:
        password = args.passwd
    else:
        password = get_password()
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
            print_child(req.simple_request('get_project_status'))
        if args.acct_mgr_attach:
            url, name, input_pwd = args.acct_mgr_attach
            req = Request(host, port, password)
            print_child(req.acct_mgr_attach(url, name, input_pwd))
        if args.lookup_account:
            url, email, input_pwd = args.lookup_account
            req = Request(host, port, password)
            auth_key = req.lookup_account(url, email, input_pwd)
            print('Authenticator: ', auth_key)
        if args.project_attach:
            url, auth = args.project_attach
            req = Request(host, port, password)
            print_child(req.project_attach(url, auth))
    except RequestValueError as exception:
        sys.exit('Error: ' + str(exception))

if __name__ == '__main__':
    main()
