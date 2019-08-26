import socket
import xml.etree.ElementTree as ET


def request_template(req):
    s = '<boinc_gui_rpc_request>{}</boinc_gui_rpc_request>\003'.format(req)
    return bytes(s, 'utf-8')

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

    def get_host_info(self):
        return self.request(request_template('<get_host_info/>'))
