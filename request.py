import socket
import xml.etree.ElementTree as ET
import hashlib


def request_template(req):
    s = '<boinc_gui_rpc_request>{}</boinc_gui_rpc_request>\003'.format(req)
    return bytes(s, 'utf-8')

#def auth2_template(req):
#    s = 

class Request(object):
    def __init__(self, host='localhost', port=31416):
        self.host = host
        self.port = port

    def __enter__(self):
        self.connect()

    def __exit__(self, type, value, traceback):
        # Check socket documentation for possible exceptions
        self.close()

    def connect(self):
        self.s = socket.create_connection((self.host, self.port))

    def close(self):
        self.s.close()

    def auth(self, password):
        xml = self.request(request_template('<auth1/>'))
        reply1 = ET.fromstring(xml)
        nonce = reply1.find('nonce').text
        # md5(nonce+password)
        m = hashlib.md5()
        m.update(nonce.encode('utf-8'))
        m.update(password.encode('utf-8'))
        md5pwd = m.hexdigest()
        #md5pwd = hashlib.md5(''.join((nonce, password)).encode('utf-8')).hexdigest()
        xml2 = self.request(request_template('<auth2><nonce_hash>{}</nonce_hash></auth2>'.format(nonce)))
        reply2 = ET.fromstring(xml2)
        return reply2

    def request(self, data):
        self.s.sendall(data)
        # [:-1] removes b'\x03' from boinc responce
        return self.s.recv(8192)[:-1]

    def get_host_info(self):
        xml = self.request(request_template('<get_host_info/>'))
        return ET.fromstring(xml)

    def exchange_versions(self):
        xml = self.request(request_template('<exchange_versions><major></major><minor></minor><release></release></exchange_versions>'))
        return ET.fromstring(xml)

    def get_state(self):
        xml = self.request(request_template('<get_state/>'))
        return ET.fromstring(xml)
