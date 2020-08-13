# request.py
#
# Copyright 2020 Yevhen Shyshkan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""This module interacts with boinc client using RPC protocol."""
import socket
import xml.etree.ElementTree as ET
import hashlib
from time import sleep

PROJECT_CHOICES = ('reset', 'detach', 'update', 'suspend', 'resume',
                   'nomorework', 'allowmorework', 'detach_when_done',
                   'dont_detach_when_done')
BUFFER_SIZE = 4096

class BoincRpcError(ValueError):
    """Provided value(s) is invalid """
    def __init__(self, msg, original_exception=None):
        super().__init__(msg)
        self.original_exception = original_exception

def et_find(el_tree, tag):
    """ Search recursively Element tree and return first match or None"""
    for element in el_tree.iter(tag):
        return element
    return None

class BoincRpc():
    """BoincRpc class is used to interact with boinc client."""

    def __init__(self, host='localhost', port=31416, password=False):
        """Create socket connection and authenticate in boinc client."""
        self.sock = None
        try:
            # Can cause at least TimeoutError, ConnectionRefusedError exceptions
            self.sock = socket.create_connection((host, port), 5)
            if not self.sock:
                raise RuntimeError('Missing socket')
        except socket.timeout as orig_ex:
            raise BoincRpcError('Cannot connect to host', orig_ex)
        except ConnectionRefusedError as orig_ex:
            raise BoincRpcError('Connection refused', orig_ex)
        # Authenticate in boinc client
        # First request
        response1 = ET.fromstring(self.simple_request('auth1'))
        # Second request
        nonce = response1.find('nonce').text
        hsh = hashlib.md5()
        # md5(nonce+password) for the second response
        hsh.update(nonce.encode('utf-8'))
        hsh.update(password.encode('utf-8'))
        md5noncepwd = hsh.hexdigest()
        xml2 = ET.Element('auth2')
        xml2_hash = ET.SubElement(xml2, 'nonce_hash')
        xml2_hash.text = md5noncepwd
        request2 = self.request(xml2)
        response2 = ET.fromstring(request2)
        if response2[0].tag == 'unauthorized':
            raise BoincRpcError('Password incorrect')

    def __del__(self):
        """Close socket connection."""
        if self.sock:
            self.sock.close()

    def request(self, data):
        """Send request to boinc client and return response."""
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
        # Recieve responce
        data = b''
        while True:
            part = self.sock.recv(BUFFER_SIZE)
            data += part
            if part[-1:] == b'\x03':
                break
        # Decode from bytes to str and remove closing tag '\x03'
        return data.decode().rstrip('\x03')

    def project_command(self, url, command):
        """Reqest template for project-related requests.

        Send request:
        <boinc_gui_rpc_request>
          <project_{{ command }}>
            <project_url>{{ url }}</project_url>
          </project_{{ command }}>
        </boinc_gui_rpc_request>\003

        Possible command values: 'reset', 'detach', 'update', 'suspend',
                                 'resume', 'nomorework',
                                 'allowmorework', 'detach_when_done',
                                 'dont_detach_when_done'
        """
        if command not in PROJECT_CHOICES:
            raise BoincRpcError('Command has illegal value')
        xml = ET.Element('project_' + command)
        xml_url = ET.SubElement(xml, 'project_url')
        xml_url.text = url
        return self.request(xml)

    def simple_request(self, element):
        """Request template for simple requests.

        Send simple request:
        <boinc_gui_rpc_request>
          <{{ element }}/>
        </boinc_gui_rpc_request>\003
        """
        xml = ET.Element(element)
        response = self.request(xml)
        return response

    def acct_mgr_attach(self, url, name, password):
        """Make an rpc to an account manager."""
        xml = ET.Element('acct_mgr_rpc')
        xml_url = ET.SubElement(xml, 'url')
        xml_name = ET.SubElement(xml, 'name')
        xml_pwd = ET.SubElement(xml, 'password')
        xml_url.text, xml_name.text, xml_pwd.text = url, name, password
        self.request(xml)
        # Second request to get results from first request
        response2 = self.simple_request('acct_mgr_rpc_poll')
        return response2

    def lookup_account(self, url, email, password):
        """look for an account in a given project. Return auth string."""
        # password_hash = md5(password + email.lower())
        hsh = hashlib.md5()
        hsh.update(password.encode('utf-8'))
        hsh.update(email.lower().encode('utf-8'))
        hsh_pwd = hsh.hexdigest()
        xml = ET.Element('lookup_account')
        xml_url = ET.SubElement(xml, 'url')
        xml_email = ET.SubElement(xml, 'email_addr')
        xml_pwd = ET.SubElement(xml, 'passwd_hash')
        xml_url.text, xml_email.text, xml_pwd.text = url, email, hsh_pwd
        self.request(xml)
        error_dict = {'-136': 'User not found',
                      '-203': 'Boinc client has no network connection',
                      '-205': 'Bad email address',
                      '-206': 'Password incorrect'}
        while True:
            # Immediate poll after first request always returns 'in progress'
            # Wait before first poll
            sleep(2)
            response = self.simple_request('lookup_account_poll')
            et_response = ET.fromstring(response)
            auth_key = et_find(et_response, 'authenticator')
            if auth_key is not None:
                break
            error = et_find(et_response, 'error_num')
            if error is not None:
                error = error.text
                if error == '-204':
                    # '-204': Operation in progress
                    continue
                if error in error_dict.keys():
                    raise BoincRpcError(error_dict[error])
            raise RuntimeError('Unknown Error ' + ET.tostring(error))
        return response

    def project_attach(self, url, auth):
        """Attach to project or raise an error."""
        xml = ET.Element('project_attach')
        xml_url = ET.SubElement(xml, 'project_url')
        xml_auth = ET.SubElement(xml, 'authenticator')
        ET.SubElement(xml, 'project_name')
        xml_url.text, xml_auth.text = url, auth
        # request1
        self.request(xml)
        # request2
        response = self.simple_request('project_attach_poll')
        # Check for common errors
        et_response = ET.fromstring(response)
        error = et_find(et_response, 'error_num')
        if error is not None and error.text == '-189':
            raise BoincRpcError('Invalid URL')
        return response
