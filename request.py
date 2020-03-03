import socket
import xml.etree.ElementTree as ET
import hashlib

def request_template(req):
    xml = '<boinc_gui_rpc_request>{}</boinc_gui_rpc_request>\003'.format(req)
    return bytes(xml, 'utf-8')

class Request():
    def __init__(self, host='localhost', port=31416, password=False):
        self.host = host
        self.port = port
        #TODO: Read password from /etc
        self.password = password

    def __enter__(self):
        self.connect()

    def __exit__(self, x_type, value, traceback):
        # Check socket documentation for possible exceptions
        self.close()

    def connect(self):
        self.sock = socket.create_connection((self.host, self.port))

    def close(self):
        self.sock.close()

    def auth(self):
        xml = self.request(request_template('<auth1/>'))
        reply1 = ET.fromstring(xml)
        nonce = reply1.find('nonce').text
        hsh = hashlib.md5()
        # md5(nonce+password) for the second reply
        hsh.update(nonce.encode('utf-8'))
        hsh.update(self.password.encode('utf-8'))
        md5noncepwd = hsh.hexdigest()
        xml2 = self.request(request_template('<auth2>'
                                             '<nonce_hash>'
                                             '{}'
                                             '</nonce_hash>'
                                             '</auth2>'.format(md5noncepwd)))
        reply2 = ET.fromstring(xml2)
        #TODO Error if not 'authorized'
        print(reply2[0].tag)

    def request(self, data):
        self.sock.sendall(data)
        # [:-1] removes b'\x03' from boinc responce
        return self.sock.recv(8192)[:-1]

    def get_host_info(self):
        xml = ET.Element('boinc_gui_rpc_request')
        ET.SubElement(xml, 'get_host_info')
        result = self.request(ET.tostring(xml) + b'\003')
        return ET.fromstring(result)

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
        xml = ET.Element('boinc_gui_rpc_request')
        ET.SubElement(xml, 'acct_mgr_info')
        xml_str = self.request(ET.tostring(xml) + b'\003')
        return ET.fromstring(xml_str)

    def acct_mgr_attach(self, url, name, password):
        self.auth()
        xml_template = (f'<acct_mgr_rpc>'
                        f'<url>{url}</url>'
                        f'<name>{name}</name>'
                        f'<password>{password}</password>'
                        f'</acct_mgr_rpc>')
        xml = self.request(request_template(xml_template))
        # Stopped because of rewrite using xml.ET
        pass
