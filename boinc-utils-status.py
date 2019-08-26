#from xmlrpc.client import ServerProxy, Error, ProtocolError
import socket
from request import Request

HOST = 'localhost'
PORT = 31416

#with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#    s.connect((HOST, PORT))
#    s.sendall(request_template('<get_host_info/>'))
#    data = s.recv(2048)

if __name__ == "__main__":
    print("Boinc utils status")
    #print('Received', repr(data))
    r = Request(HOST, PORT)
    r.connect()
    print(repr(r.get_host_info()))
    r.close()
