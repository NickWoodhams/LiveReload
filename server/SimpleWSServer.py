#!/usr/bin/python
# -*- coding: utf-8 -*-


class SimpleWSServer(object):

    """SimpleWSServer"""

    def __init__(self):
        try:
            if not self.ws_callbacks:
                self.ws_callbacks = []
        except Exception, e:
            self.ws_callbacks = []

    def has_ws_callback(self, path):
        """Traverse added static_files return object"""

        print 'testing for path %s' % path
        for callback in self.ws_callbacks:
            print 'looking %s' % callback['path']
            if path in callback['path']:
                print 'found path %s' % callback['path']
                return callback
        return False