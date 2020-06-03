# Boinc RPC
Python implementation of the [BOINC GUI RPC protocol](http://boinc.berkeley.edu/trac/wiki/GuiRpc).

`boincrpc.py` is a module that contains BoincRpc

`cmd.py` is a command-line script simmilar to the boinccmd

## Requirements
Python >= 3.6
Does not require any external libraries.

## Usage

### boincrpc

```python
from boincrpc import BoincRpc, BoincRpcError

try:
    boinc_rpc = BoincRpc('localhost', 31416, BOINC_PASSWORD)
        xml = boinc_rpc.simple_request('get_project_status')
except BoincRpcError as exception:
    print('Error:' + str(exception))
```

### cmd.py

```shell
./cmd.py --client_version
major: 7
minor: 14
release: 2
```

## License
LGPL 3+
