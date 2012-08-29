#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import json
import sublime


class Settings(dict):

    def __init__(self):
        self.file_name = os.path.join(sublime.packages_path(), 'LiveReload',
                                      'LiveReload.sublime-settings')
        file_object = open(self.file_name)
        data = json.load(file_object)
        file_object.close()
        for i in range(len(data)):
            self[data.keys()[i]] = data[data.keys()[i]]
        print 'LiveReload: Settings loaded'

    def save(self):
        file_object = open(self.file_name, 'w')
        json.dump(self, file_object, indent=5)
        file_object.close()
        print 'LiveReload: Settings saved'

    def get(self, key, default=None):
        try:
            return self[key]
        except Exception:
            return default

    def set(self, key, value):
        self[key] = value
        self.save()

    def reload(self):
        self.__init__(self.file_name)
