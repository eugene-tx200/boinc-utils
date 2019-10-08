import socket
from request import Request
import xml.etree.ElementTree as ET


HOST = 'localhost'
PORT = 31416
# Password stored in /etc/boinc-client/gui_rpc_auth.cfg
PASSWORD = 'G3d2H5z1M7'

def print_child(data):
    for child in data:
        print ('{}: {}'.format(child.tag, child.text))
        if child:
            print_child(child)

def get_host_info():
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

def exchange_versions():
    r = Request(HOST, PORT)
    with r:
        data = r.exchange_versions()
        print_child(data)

def get_state():
    r = Request(HOST, PORT)
    with r:
        data = r.get_state()
        print_child(data)

def acct_mgr_info():
    r = Request(HOST, PORT)
    with r:
        data = r.auth(PASSWORD)
        print_child(data)
