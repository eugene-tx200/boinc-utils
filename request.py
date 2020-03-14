import socket
import xml.etree.ElementTree as ET
import hashlib


class Request():
    def __init__(self, host='localhost', port=31416, password=False):
        self.host = host
        self.port = port
        #TODO: Read password from /etc
        self.password = password

    def __enter__(self):
        self.sock = socket.create_connection((self.host, self.port))

    def __exit__(self, x_type, value, traceback):
        # Check socket documentation for possible exceptions
        self.sock.close()

    def auth(self):
        # First request
        xml = ET.Element('boinc_gui_rpc_request')
        ET.SubElement(xml, 'auth1')
        request = self.request(xml)
        reply1 = ET.fromstring(request)
        # Second request
        nonce = reply1.find('nonce').text
        hsh = hashlib.md5()
        # md5(nonce+password) for the second reply
        hsh.update(nonce.encode('utf-8'))
        hsh.update(self.password.encode('utf-8'))
        md5noncepwd = hsh.hexdigest()
        xml2 = ET.Element('boinc_gui_rpc_request')
        xml2_auth = ET.SubElement(xml2, 'auth2')
        xml2_hash = ET.SubElement(xml2_auth, 'nonce_hash')
        xml2_hash.text = md5noncepwd
        reply2 = self.request(xml2)
        #TODO Error if not 'authorized'

    def request(self, data):
        # Convert xml to bytes
        if type(data) == str:
            data = bytes(data, 'utf8')
        elif type(data) == ET.Element:
            data = ET.tostring(data)
        # Remove spaces before /
        data = data.replace(b' /', b'/')
        # Add closing tag
        data += b'\003'
        self.sock.sendall(data)
        # [:-1] removes closing tag '\x03' from boinc responce
        return self.sock.recv(8192)[:-1]

    def get_host_info(self):
        xml = ET.Element('boinc_gui_rpc_request')
        ET.SubElement(xml, 'get_host_info')
        reply = self.request(xml)
        return ET.fromstring(reply)

    def exchange_versions(self):
        xml = ET.Element('boinc_gui_rpc_request')
        ET.SubElement(xml, 'exchange_versions')
        reply = self.request(xml)
        return ET.fromstring(reply)

    def get_state(self):
        xml = ET.Element('boinc_gui_rpc_request')
        ET.SubElement(xml, 'get_state')
        reply = self.request(xml)
        return ET.fromstring(reply)

    def acct_mgr_info(self):
        self.auth()
        xml = ET.Element('boinc_gui_rpc_request')
        ET.SubElement(xml, 'acct_mgr_info')
        reply = self.request(xml)
        return ET.fromstring(reply)

    def acct_mgr_attach(self, url, name, password):
        self.auth()
        xml = ET.Element('boinc_gui_rpc_request')
        xml_amr = ET.SubElement(xml, 'acct_mgr_rpc')
        xml_url = ET.SubElement(xml_amr, 'url')
        xml_name = ET.SubElement(xml_amr, 'name') 
        xml_pwd = ET.SubElement(xml_amr, 'password')
        xml_url.text, xml_name.text, xml_pwd.text = url, name, password 
        reply = self.request(xml)
        # Second request to get results from first request
        xml2 = ET.Element('boinc_gui_rpc_request')
        ET.SubElement(xml, 'acct_mgr_rpc_poll')
        reply2 = self.request(xml2)
        return ET.fromstring(reply2)
