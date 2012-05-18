#!/usr/bin/python
# -*- coding: utf-8 -*-

import sublime
import urllib2
import os
import sys
import threading
import atexit
from WebSocketServer import WebSocketServer
from SimpleResourceServer import SimpleResourceServer
from LiveReloadAPI import LiveReloadAPI
from PluginAPI import PluginClass as Plugin

def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance


@singleton
class LiveReload(threading.Thread, SimpleResourceServer, LiveReloadAPI):

    """
    Start the LiveReload, which exposes public api.
    """

    def run(self):
        """
        Start LiveReload
        """

        threading.Thread.__init__(self)
        SimpleResourceServer.__init__(self)
        LiveReloadAPI.__init__(self)

        # LOAD latest livereload.js from github (for v2 of protocol) or if this fails local version

        try:
            req = \
                urllib2.urlopen(urllib2.Request('http://raw.github.com/livereload/livereload-js/master/dist/livereload.js'
                                ))

            if not 'http://livereload.com/protocols/official-6' \
                in req.read():
                raise Exception('livereload.js updating failed, using bundled version'
                                )
            else:
                self.add_static_file('/livereload.js', req.read(),
                        'text/javascript')
        except Exception, u:
            print u
            try:
                path = os.path.join(sublime.packages_path(),
                                    'LiveReload', 'web', 'livereload.js'
                                    )
                local = open(path, 'rU')
                self.add_static_file('/livereload.js', local.read(),
                        'text/javascript')
            except IOError, e:
                print e
                sublime.error_message('livereload.js is missing from LiveReload package install'
                        )

        try:
            self.start_server(self.port)
        except Exception:
            sublime.error_message('Port(' + str(self.port)
                                  + ') is allready using, trying ('
                                  + str(self.port + 1) + ')')
            self.start_server(self.port + 1)

    def start_server(self, port):
        """
        Start the server.
        """

        self.ws_server = WebSocketServer(port, self.version)
        self.ws_server.start()

    @atexit.register
    def clean(self):
        """
        Stop the server.
        """

        self.ws_server.stop()


try:
    sys.modules['LiveReload'].API
except Exception:
    API = LiveReload()
    API.start()
