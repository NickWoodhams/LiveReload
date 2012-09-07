#!/usr/bin/python
# -*- coding: utf-8 -*-


class SimpleCallbackServer(object):

    """SimpleCallbackServer"""

    def __init__(self):
        try:
            if not self.callbacks:
                self.callbacks = []
        except Exception, e:
            self.callbacks = []

    def has_callback(self, path):
        """Traverse added static_files return object"""

        print 'testing for path %s' % path
        for callback in self.callbacks:
            print 'looking %s' % callback['path']
            if path in callback['path']:
                print 'found path %s' % callback['path']
                return callback
        return False