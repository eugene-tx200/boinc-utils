import socket
import xml.etree.ElementTree as ET
from utils import request_template


class Request(object):
    def __init__(self, host='localhost', port=31416):
        self.host = host
        self.port = port

    def connect(self):
        self.s = socket.create_connection((self.host, self.port))

    def close(self):
        self.s.close()

    def request(self, data):
        self.s.sendall(data)
        return self.s.recv(2048)
