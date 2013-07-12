#!/usr/bin/python
# -*- coding: utf-8 -*-

import sublime
import os
import sys
import threading
import atexit
import time
import logging

try:

    # Python 3

    from .server.WebSocketServer import WebSocketServer
    from .server.SimpleResourceServer import SimpleResourceServer
    from .server.SimpleCallbackServer import SimpleCallbackServer
    from .server.LiveReloadAPI import LiveReloadAPI
    from .server.PluginAPI import PluginInterface as Plugin
    from .server.Settings import Settings
except ValueError:

    # Python 2

    from server.WebSocketServer import WebSocketServer
    from server.SimpleResourceServer import SimpleResourceServer
    from server.SimpleCallbackServer import SimpleCallbackServer
    from server.LiveReloadAPI import LiveReloadAPI
    from server.PluginAPI import PluginInterface as Plugin
    from server.Settings import Settings


logging.basicConfig(level=logging.INFO)
log = logging.getLogger('LiveReload')

def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance

@singleton
class LiveReload(threading.Thread, SimpleCallbackServer,
    SimpleResourceServer, LiveReloadAPI):

    """
    Start the LiveReload, which exposes public api.
    """

    def __init__(self):

        threading.Thread.__init__(self)
        SimpleCallbackServer.__init__(self)
        SimpleResourceServer.__init__(self)
        LiveReloadAPI.__init__(self)

    def run(self):
        """
        Start LiveReload
        """

        livereloadjs = open(os.path.join(sublime.packages_path(), 'LiveReload', 'web'
                            , 'dist', 'livereloadjs-sm2.js'), 'rU')

        self.add_static_file('/livereload.js', livereloadjs.read(), 'text/javascript')

        index_doc = open(os.path.join(sublime.packages_path(), 'LiveReload', 'web'
                            , 'test.html'), 'rU')

        self.add_static_file('/index.html', index_doc.read(), 'text/html')

        settings = Settings()
        self.port = settings.get('port', 35729)
        self.version = settings.get('version', '2.0')

        try:
            self.start_server(self.port)
        except Exception as e:
            log.exception("Port used")
            sublime.error_message('Port(' + str(self.port)
                                  + ') is already using, trying ('
                                  + str(self.port + 1) + ')')
            time.sleep(3)
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


if not sublime.platform is 'build':
    try:
        sys.modules['LiveReload'].API
    except Exception:
        API = LiveReload()
        API.start()


def http_callback(callback_f):
    """
    Add http callback to plugin defined function. For example request to GET /callback/plugin_name/log_me
    would trigger log_me function in plugin

    Example:
    ::

        @LiveReload.http_callback
        def compiled(self, req):
            print req # urlparse object
            return "cool" #to http client

    """

    callback_f.path = 'http://localhost:35729/callback/%s/%s' \
        % (callback_f.__module__.lower(), callback_f.__name__)
    sys.modules['LiveReload'
                ].API.callbacks.append({'path': callback_f.path,
            'name': callback_f.__name__, 'cls': callback_f.__module__})
    log.info(callback_f.path)
    return callback_f
