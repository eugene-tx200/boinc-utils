from xmlrpc.client import ServerProxy, Error, ProtocolError

proxy = ServerProxy("http://127.0.0.1:31416")
try:
    proxy.system.listMethods()
except ProtocolError as err:
    print("A protocol error occurred")
    print("Error code: %d" % err.errcode)


if __name__ == "__main__":
    print("Boinc utils status")
