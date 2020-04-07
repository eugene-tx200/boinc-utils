"""This module interacts with boinc client using RPC protocol."""
import socket
import xml.etree.ElementTree as ET
import hashlib


class Request():
    """Request class is used to interact with boinc client."""

    def __init__(self, host='localhost', port=31416, password=False):
        """Create socket connection and authenticate in boinc client."""
        self.sock = None
        # Can cause at least TimeoutError, ConnectionRefusedError exceptions
        self.sock = socket.create_connection((host, port), 5)
        if not self.sock:
            raise RuntimeError('Missing socket')
        # Authenticate in boinc client
        # First request
        reply1 = self.simple_request('auth1')
        # Second request
        nonce = reply1.find('nonce').text
        hsh = hashlib.md5()
        # md5(nonce+password) for the second reply
        hsh.update(nonce.encode('utf-8'))
        hsh.update(password.encode('utf-8'))
        md5noncepwd = hsh.hexdigest()
        xml2 = ET.Element('auth2')
        xml2_hash = ET.SubElement(xml2, 'nonce_hash')
        xml2_hash.text = md5noncepwd
        request2 = self.request(xml2)
        reply2 = ET.fromstring(request2)
        if reply2[0].tag == 'unauthorized':
            raise RuntimeError('Unauthorized')

    def __del__(self):
        """Close socket connection."""
        if self.sock:
            self.sock.close()

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
        #print('Request:', xml_str)
        self.sock.sendall(xml_str)
        # [:-1] removes closing tag '\x03' from boinc responce
        responce = self.sock.recv(65536)[:-1]
        #print('Responce:', responce)
        return responce

    def simple_request(self, element):
        """Request template for simple requests.

        Send simple request:
        <boinc_gui_rpc_request>
          <{{ element }}/>
        </boinc_gui_rpc_request>\003
        Return is an ET object
        """
        xml = ET.Element(element)
        reply = self.request(xml)
        return ET.fromstring(reply)

    def acct_mgr_attach(self, url, name, password):
        """Make an rpc to an account manager."""
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
