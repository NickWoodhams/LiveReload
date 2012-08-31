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
from server.SimpleCallbackServer import SimpleCallbackServer
from server.LiveReloadAPI import LiveReloadAPI
from server.PluginAPI import PluginClass as Plugin
from server.Settings import Settings


def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            print 'new instance of', cls.__name__
            instances[cls] = cls()
        return instances[cls]

    return getinstance


class LiveReload(threading.Thread, SimpleCallbackServer, SimpleResourceServer, LiveReloadAPI):

    """
    Start the LiveReload, which exposes public api.
    """

    def run(self):
        """
        Start LiveReload
        """

        threading.Thread.__init__(self)
        SimpleCallbackServer.__init__(self)
        SimpleResourceServer.__init__(self)
        LiveReloadAPI.__init__(self)

        path = os.path.join(sublime.packages_path(), 'LiveReload', 'web', 'livereload.js')
        local = open(path, 'rU')
        self.add_static_file('/livereload.js', local.read(), 'text/javascript')

        settings = Settings()
        self.port = settings.get('port', 35729)
        self.version = settings.get('version', '2.0')

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


class http_callback(object):

    """
    Add callback to plugin defined function. For example request to GET /callback/plugin_name/log_me
    would trigger log_me function in plugin

    Example:
        @LiveReload.http_callback
        def compiled(self, req):
            print req # urlparse object
            return "cool" #to http client

    """

    def __init__(self, callback_f):

        path = '/callback/%s/%s' % (callback_f.__module__, callback_f.__name__)
        print 'LiveReload: added callback with url %s' % path
        callback_f.path = path
        sys.modules['LiveReload'].API.callbacks.append({'path': path, 'callback': self})
        self.func = callback_f

    def __call__(self, req):
        return self.func(self, req)

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        new_func = self.func.__get__(obj, type)
        return self.__class__(new_func)
