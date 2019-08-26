#from xmlrpc.client import ServerProxy, Error, ProtocolError
import socket
from request import Request

import xml.etree.ElementTree as ET


HOST = 'localhost'
PORT = 31416

if __name__ == "__main__":
    print("Boinc utils status")
    r = Request(HOST, PORT)
    r.connect()
    data = r.get_host_info()
    # ugly example
    print(ET.tostring(data).decode())
    r.close()
