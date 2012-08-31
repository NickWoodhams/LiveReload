#!/usr/bin/python
# -*- coding: utf-8 -*-


class SimpleCallbackServer(object):

    """SimpleCallbackServer"""

    def __init__(self):
        self.callbacks = []

    def has_callback(self, path):
        """Traverse added static_files return object"""

        for callback in self.callbacks:
            if path == callback['path']:
                return callback['callback']
        return False
