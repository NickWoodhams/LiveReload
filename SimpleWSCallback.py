#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import sublime
import sublime_plugin

# fix for import order

sys.path.append(os.path.join(sublime.packages_path(), 'LiveReload'))
LiveReload = __import__('LiveReload')
sys.path.remove(os.path.join(sublime.packages_path(), 'LiveReload'))

##Modlue name must be the same as class or else callbacks won't work
class SimpleWSCallback(LiveReload.Plugin, sublime_plugin.EventListener):

    title = 'Send content on change'
    description = \
        'Send file content to browser console'
    file_types = '*'
    this_session_only = True

    def on_modified_async(self, view):
      print(self)
      print(view)
      source = view.file_name()
      with open(source, 'rU') as f:
        self.sendRaw("socket", f.read())
        
    def onReceive(self, data, origin):
      print(data)