#from xmlrpc.client import ServerProxy, Error, ProtocolError
import socket
from utils import request_template

HOST = 'localhost'
PORT = 31416

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(request_template('<get_host_info/>'))
    data = s.recv(2048)

if __name__ == "__main__":
    print("Boinc utils status")
    print('Received', repr(data))
