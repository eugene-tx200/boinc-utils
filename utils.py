def request_template(req):
    s = '<boinc_gui_rpc_request>{}</boinc_gui_rpc_request>\003'.format(req)
    return bytes(s, 'utf-8')
