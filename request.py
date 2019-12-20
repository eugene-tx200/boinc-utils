import socket
import xml.etree.ElementTree as ET
import hashlib

def request_template(req):
    s = '<boinc_gui_rpc_request>{}</boinc_gui_rpc_request>\003'.format(req)
    return bytes(s, 'utf-8')

#def auth2_template(req):
#    s = 

class Request(object):
    def __init__(self, host='localhost', port=31416, password=False):
        self.host = host
        self.port = port
        #TODO: Read password from /etc
        self.password = password

    def __enter__(self):
        self.connect()

    def __exit__(self, type, value, traceback):
        # Check socket documentation for possible exceptions
        self.close()

    def connect(self):
        self.s = socket.create_connection((self.host, self.port))

    def close(self):
        self.s.close()

    def auth(self):
        xml = self.request(request_template('<auth1/>'))
        reply1 = ET.fromstring(xml)
        nonce = reply1.find('nonce').text
        m = hashlib.md5()
        m.update(''.join((nonce, self.password)).encode('utf-8'))
        md5noncepwd = m.hexdigest()
        xml2 = self.request(request_template('<auth2>'
                                             '<nonce_hash>'
                                             '{}'
                                             '</nonce_hash>'
                                             '</auth2>'.format(md5noncepwd)))
        reply2 = ET.fromstring(xml2)
        #TODO Error if not 'authorized' 
        print(reply2[0].tag)
        
    def request(self, data):
        self.s.sendall(data)
        # [:-1] removes b'\x03' from boinc responce
        return self.s.recv(8192)[:-1]

    def get_host_info(self):
        xml = self.request(request_template('<get_host_info/>'))
        return ET.fromstring(xml)

    def exchange_versions(self):
        xml = self.request(request_template('<exchange_versions>'
                                            '<major></major>'
                                            '<minor></minor>'
                                            '<release></release>'
                                            '</exchange_versions>'))
        return ET.fromstring(xml)

    def get_state(self):
        xml = self.request(request_template('<get_state/>'))
        return ET.fromstring(xml)

    def acct_mgr_info(self):
        self.auth()
        xml = self.request(request_template('<acct_mgr_info/>'))
        return ET.fromstring(xml)
