"""This module interacts with boinc client using RPC protocol."""
import socket
import xml.etree.ElementTree as ET
import hashlib
from time import sleep


class RequestValueError(ValueError):
    """Provided value(s) is invalid """

def req_find(el_tree, tag):
    """ Search recursivly Element tree and return first match or None"""
    for el in el_tree.iter(tag):
        return el
    return None

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
        reply2 = self.simple_request('acct_mgr_rpc_poll')
        return reply2

    def lookup_account(self, url, email, password):
        """look for an account in a given project. Return auth string."""
        # password_hash = md5(password + email.lower())
        hsh = hashlib.md5()
        hsh.update(password.encode('utf-8'))
        hsh.update(email.lower().encode('utf-8'))
        pwd_hsh = hsh.hexdigest()
        xml = ET.Element('lookup_account')
        xml_url = ET.SubElement(xml, 'url')
        xml_email = ET.SubElement(xml, 'email_addr')
        xml_pwd = ET.SubElement(xml, 'passwd_hash')
        xml_url.text, xml_email.text, xml_pwd.text = url, email, pwd_hsh
        self.request(xml)
        err_dict = {'-136': 'User not found',
                    '-203': 'Boinc client has no network connection',
                    '-205': 'Bad email address',
                    '-206': 'Wrong password'}
        while True:
            # Immediate poll after first request always returns 'in progress'
            # Wait before first poll
            sleep(2)
            reply2 = self.simple_request('lookup_account_poll')
            auth_key = req_find(reply2, 'authenticator')
            if auth_key != None:
                break
            err = req_find(reply2, 'error_num')
            if err != None:
                err_no = err.text
                if err_no == '-204':
                    # '-204': Operation in progress
                    continue
                if err_no in err_dict.keys():
                    raise RequestValueError(err_dict[err_no])
            raise RuntimeError('Unknown Error ' + ET.tostring(err))
        return auth_key.text
