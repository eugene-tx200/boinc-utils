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


class BoincRpcError(ValueError):
    """Provided value(s) is invalid """
    def __init__(self, msg, original_exception=None):
        super().__init__(msg)
        self.original_exception = original_exception

def req_find(el_tree, tag):
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
            raise BoincRpcError('Password incorrect')

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
        self.sock.sendall(xml_str)
        # [:-1] remove closing tag '\x03' from boinc responce
        responce = self.sock.recv(65536)[:-1]
        return responce

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
        Return is an ET object
        """
        if command not in PROJECT_CHOICES:
            raise BoincRpcError('Command has illegal value')
        xml = ET.Element('project_' + command)
        xml_url = ET.SubElement(xml, 'project_url')
        xml_url.text = url
        ET.dump(xml)
        reply = self.request(xml)
        print(reply)
        return ET.fromstring(reply)

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
        error_dict = {'-136': 'User not found',
                      '-203': 'Boinc client has no network connection',
                      '-205': 'Bad email address',
                      '-206': 'Password incorrect'}
        while True:
            # Immediate poll after first request always returns 'in progress'
            # Wait before first poll
            sleep(2)
            reply2 = self.simple_request('lookup_account_poll')
            auth_key = req_find(reply2, 'authenticator')
            if auth_key is not None:
                break
            error = req_find(reply2, 'error_num')
            if error is not None:
                error = error.text
                if error == '-204':
                    # '-204': Operation in progress
                    continue
                if error in error_dict.keys():
                    raise BoincRpcError(error_dict[error])
            raise RuntimeError('Unknown Error ' + ET.tostring(error))
        return auth_key.text

    def project_attach(self, url, auth):
        """Attach to project. Return ?? or raise an error."""
        xml = ET.Element('project_attach')
        xml_url = ET.SubElement(xml, 'project_url')
        xml_auth = ET.SubElement(xml, 'authenticator')
        ET.SubElement(xml, 'project_name')
        xml_url.text, xml_auth.text = url, auth
        reply1 = self.request(xml)
        print('Reply1: ', reply1)
        reply2 = self.simple_request('project_attach_poll')
        ET.dump(reply2)
        return reply2
