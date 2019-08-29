import socket
from request import Request
import xml.etree.ElementTree as ET


HOST = 'localhost'
PORT = 31416

def print_child(data):
    for child in data:
        print ('{}: {}'.format(child.tag, child.text))
        if child:
            print_child(child)

def get_host_info():
    r = Request(HOST, PORT)
    r.connect()
    data = r.get_host_info()
    print_child(data)
    r.close()

def exchange_versions():
    r = Request(HOST, PORT)
    r.connect()
    data = r.exchange_versions()
    print_child(data)
    r.close()
