#!/usr/bin/env python3
#
# cmd.py
#
# Copyright 2020 Yevhen Shyshkan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Utility to control boinc-client. Copycat of the boinccmd"""
import argparse
import sys
import xml.etree.ElementTree as ET
from request import Request, RequestValueError, PROJECT_CHOICES


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

def get_parser():
    """ Return parser simmilar to the boinccmd command."""
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
    parser.add_argument('--project', nargs=2, metavar=('URL', 'op'),
                        help='project operation. op = ' + str(PROJECT_CHOICES))
    return parser

def main():
    """ Main Function. Intended to run from command line"""
    parser = get_parser()
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
        req = Request(host, port, password)
        if args.get_host_info:
            print_child(req.simple_request('get_host_info'))
        if args.client_version:
            print_child(req.simple_request('exchange_versions'))
        if args.get_state:
            print_child(req.simple_request('get_state'))
        if args.acct_mgr_info:
            print_child(req.simple_request('acct_mgr_info'))
        if args.get_project_status:
            print_child(req.simple_request('get_project_status'))
        if args.acct_mgr_attach:
            url, name, input_pwd = args.acct_mgr_attach
            print_child(req.acct_mgr_attach(url, name, input_pwd))
        if args.lookup_account:
            url, email, input_pwd = args.lookup_account
            auth_key = req.lookup_account(url, email, input_pwd)
            print('Authenticator: ', auth_key)
        if args.project_attach:
            url, auth = args.project_attach
            print_child(req.project_attach(url, auth))
        if args.project:
            url, command = args.project
            if command not in PROJECT_CHOICES:
                sys.exit('Error: Illegal op value. Possible op values: '
                         + str(PROJECT_CHOICES))
            print_child(req.project_command(url, command))
    except RequestValueError as exception:
        sys.exit('Error: ' + str(exception))

if __name__ == '__main__':
    main()
