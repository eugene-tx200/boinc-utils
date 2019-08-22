#from xmlrpc.client import ServerProxy, Error, ProtocolError
import socket


HOST = 'localhost'
PORT = 31416

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'<boinc_gui_rpc_request><get_host_info/></boinc_gui_rpc_request>\003')
    data = s.recv(2048)

if __name__ == "__main__":
    print("Boinc utils status")
    print('Received', repr(data))
    
