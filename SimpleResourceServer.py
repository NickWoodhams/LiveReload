#!/usr/bin/python
# -*- coding: utf-8 -*-

class SimpleResourceServer(object):

    """SimpleResourceServer"""

    def __init__(self):
        super(SimpleResourceServer, self).__init__()
        self.static_files = []

    def has_file(self, path):
        """Traverse added static_files return object"""
        for file in self.static_files:
            if path == file["path"]:
                return file
        return False
