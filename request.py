"""This module interacts with boinc client using RPC protocol."""
import socket
import xml.etree.ElementTree as ET
import hashlib
import sys


class Request():
    """Request class is used to interact with boinc client."""
    def __init__(self, host='localhost', port=31416, password=False):
        """ Class constructor. Open socket connection."""
        self.host = host
        self.port = port
        self.password = password
        self.sock = None
        try:
            self.sock = socket.create_connection((host, port), 5)
        except TimeoutError:
            #print('Error: Connection timed out')
            sys.exit('Error: Connection timed out')
        except ConnectionRefusedError:
            sys.exit('Error: Connection refused')

    def __del__(self):
        """Class desructor. Close socket connection."""
        if self.sock:
            self.sock.close()

    def auth(self):
        """Authenticate in boinc client."""
        # First request
        xml = ET.Element('auth1')
        request = self.request(xml)
        reply1 = ET.fromstring(request)
        # Second request
        nonce = reply1.find('nonce').text
        hsh = hashlib.md5()
        # md5(nonce+password) for the second reply
        hsh.update(nonce.encode('utf-8'))
        hsh.update(self.password.encode('utf-8'))
        md5noncepwd = hsh.hexdigest()
        xml2 = ET.Element('auth2')
        xml2_hash = ET.SubElement(xml2, 'nonce_hash')
        xml2_hash.text = md5noncepwd
        #reply2 = self.request(xml2)
        self.request(xml2)
        # TODO Error if not 'authorized'

    def request(self, data):
        """Send request to boinc client and return responce."""
        xml = ET.Element('boinc_gui_rpc_request')
        # Convert data to ET
        if isinstance(data, str):
            data = ET.fromstring(data)
        xml.append(data)
        xml_str = ET.tostring(xml)
        xml_str = xml_str.replace(b' /', b'/')
        # Add closing tag
        xml_str += b'\003'
        self.sock.sendall(xml_str)
        # [:-1] removes closing tag '\x03' from boinc responce
        return self.sock.recv(8192)[:-1]

    def get_host_info(self):
        """Get information about host hardware and usage."""
        self.auth()
        xml = ET.Element('get_host_info')
        reply = self.request(xml)
        return ET.fromstring(reply)

    def exchange_versions(self):
        """Get the version of the running core client."""
        self.auth()
        xml = ET.Element('exchange_versions')
        reply = self.request(xml)
        return ET.fromstring(reply)

    def get_state(self):
        """Get the entire state of the running client."""
        self.auth()
        xml = ET.Element('get_state')
        reply = self.request(xml)
        return ET.fromstring(reply)

    def acct_mgr_info(self):
        """Retrieve account manager information."""
        self.auth()
        xml = ET.Element('acct_mgr_info')
        reply = self.request(xml)
        return ET.fromstring(reply)

    def get_project_init_status(self):
        self.auth()
        """ Get the contents of the project_init.xml file if present"""
        xml = ET.Element('get_project_init_status')
        reply = self.request(xml)
        return ET.fromstring(reply)

    def acct_mgr_attach(self, url, name, password):
        """Make an rpc to an account manager."""
        self.auth()
        xml = ET.Element('acct_mgr_rpc')
        xml_url = ET.SubElement(xml, 'url')
        xml_name = ET.SubElement(xml, 'name')
        xml_pwd = ET.SubElement(xml, 'password')
        xml_url.text, xml_name.text, xml_pwd.text = url, name, password
        self.request(xml)
        # Second request to get results from first request
        xml2 = ET.Element('acct_mgr_rpc_poll')
        reply2 = self.request(xml2)
        return ET.fromstring(reply2)
