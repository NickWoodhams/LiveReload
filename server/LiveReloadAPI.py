#!/usr/bin/python
# -*- coding: utf-8 -*-

import sublime
from Settings import Settings
from functools import wraps


class LiveReloadAPI(object):

    """Official LiveReloadAPI for SM2"""

    def __init__(self):
        super(LiveReloadAPI, self).__init__()
        self.callbacks = []

    def add_static_file(
        self,
        path,
        buffer,
        content_type,
        ):
        """
        Adds resource to embedded http server
          path (string) request uri
          buffer (string) or (file) object
          content_type (string) mime type of the object to be served
        Example:

          LiveReload.API.add_static_file('/helloworld.js', "alert('Helloworld!')",
                                'text/javascript')
        """

        print 'LiveReload: added file ' + path + ' with content-type: ' + str(content_type)
        self.static_files.append({'path': path, 'buffer': buffer, 'content_type': content_type})

    def send(self, data):
        """
        Send json encoded command to all clients
        Example:

          data = json.dumps(["refresh", {
                "path": filename,
                "apply_js_live": False,
                "apply_css_live": False,
                "apply_images_live": False
          }])

          LiveReload.API.send(data)
        """

        self.ws_server.send(data)

    def list_clients(self):
        """
        Return list with connected clients with origin and url
        Example:

          [
            {
              origin: "chrome-extension://jnihajbhpnppcggbcgedagnkighmdlei",
              url: "https://chrome.google.com/webstore/search/livereload"
            }
          ]
        """

        return self.ws_server.server.list_clients()