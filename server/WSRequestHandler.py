#!/usr/bin/python
# -*- coding: utf-8 -*-

from SimpleHTTPServer import SimpleHTTPRequestHandler
import LiveReload
import urlparse
import sys

# HTTP handler with WebSocket upgrade support

class WSRequestHandler(SimpleHTTPRequestHandler):

    def __init__(
        self,
        req,
        addr,
        only_upgrade=True,
        ):

        self.only_upgrade = only_upgrade  # only allow upgrades
        SimpleHTTPRequestHandler.__init__(self, req, addr, object())

        # self.server_version = 'LiveReload/1.0'

    def do_GET(self):
        if self.headers.get('upgrade') and self.headers.get('upgrade').lower() == 'websocket':

            if self.headers.get('sec-websocket-key1') or self.headers.get('websocket-key1'):

                # For Hixie-76 read out the key hash

                self.headers.__setitem__('key3', self.rfile.read(8))

            # Just indicate that an WebSocket upgrade is needed

            self.last_code = 101
            self.last_message = '101 Switching Protocols'
        elif self.only_upgrade:

            # Normal web request responses are disabled

            self.last_code = 405
            self.last_message = '405 Method Not Allowed'
        else:
            req = urlparse.urlparse(self.path)
            _file = LiveReload.API.has_file(req.path)
            _httpcallback = LiveReload.API.has_callback(req.path)

            if _httpcallback:
                try:
                    func = getattr(sys.modules['LiveReload'].Plugin.getPlugin(_httpcallback['cls']), _httpcallback['name'], None)
                    if func:
                        res = func(req)
                        self.send_response(200, 'OK')
                    else:
                        res = "Callback method not found"
                        self.send_response(404, 'Not Found')
                    print res
                except Exception, e:
                    print e
                    self.send_response(500, 'Error')
                    res = e
                
                self.send_header('Content-type', 'text/plain')
                self.send_header('Content-Length', len(res))
                self.end_headers()
                self.wfile.write(bytes(res))
                return
            elif _file:
                if isinstance(_file['buffer'], file):
                    buffer = _file['buffer'].read()
                else:
                    buffer = _file['buffer']

                self.send_response(200, 'OK')
                self.send_header('Content-type', _file['content_type'])
                self.send_header('Content-Length', len(buffer))
                self.end_headers()
                self.wfile.write(bytes(buffer))
                return
            else:

                # Disable other requests

                self.send_response(404, 'Not Found')
                self.send_header('Content-type', 'text/plain')
                self.send_header('Content-Length', len('Method Not Allowed'))
                self.end_headers()
                self.wfile.write(bytes('Method Not Allowed'))
                return

    def send_response(self, code, message=None):

        # Save the status code

        self.last_code = code
        SimpleHTTPRequestHandler.send_response(self, code, message)

    def log_message(self, f, *args):

        # Save instead of printing

        self.last_message = f % args
