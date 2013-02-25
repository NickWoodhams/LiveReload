#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import json

def log(msg):
    pass

try:
    import sublime
except Exception as e:
    log(e)


class Settings(dict):

    def __init__(self):
        try:
            cdir = os.path.dirname(os.path.abspath(__file__))
            if not "LiveReload" in cdir:
                cdir = os.path.join(sublime.packages_path(), 'LiveReload')
            self.file_name = os.path.join(cdir, '..',
                                          'LiveReload.sublime-settings')
            file_object = open(self.file_name)
            data = json.load(file_object)
            file_object.close()
            for i in range(len(data)):
                self[data.keys()[i]] = data[data.keys()[i]]
            log('LiveReload: Settings loaded')
        except Exception as e:
            log(e)
            
    def save(self):
        file_object = open(self.file_name, 'w')
        json.dump(self, file_object, indent=5)
        file_object.close()
        log('LiveReload: Settings saved')

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
