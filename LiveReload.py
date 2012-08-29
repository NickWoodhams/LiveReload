#!/usr/bin/python
# -*- coding: utf-8 -*-

import sublime
import urllib2
import os
import sys
import threading
import atexit

from server.WebSocketServer import WebSocketServer
from server.SimpleResourceServer import SimpleResourceServer
from server.LiveReloadAPI import LiveReloadAPI
from server.PluginAPI import PluginClass as Plugin
from server.Settings import Settings

def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            print "new instance of", cls.__name__
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

        path = os.path.join(sublime.packages_path(), 'LiveReload', 'web', 'livereload.js')
        local = open(path, 'rU')
        self.add_static_file('/livereload.js', local.read(), 'text/javascript')

        settings = Settings()
        self.port = settings.get("port", 35729)
        self.version = settings.get("version", "2.0")
        
        try:
            self.start_server(self.port)
        except Exception:
            sublime.error_message('Port(' + str(self.port) + ') is allready using, trying ('
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
