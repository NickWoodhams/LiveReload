#!/usr/bin/python
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
import os
import sys

# fix for import order

sys.path.append(os.path.join(sublime.packages_path(), 'LiveReload'))
LiveReload = __import__('LiveReload')
sys.path.remove(os.path.join(sublime.packages_path(), 'LiveReload'))


class SimpleReloadOnCompile(LiveReload.Plugin, sublime_plugin.EventListener):

    title = 'Reload on build (via SM2 build)'
    description = "Reload when SM2 native build finishes it's task"
    file_types = '*'

    def on_compile(self):
        self.refresh(os.path.basename(sublime.active_window().active_view().file_name()))

    def __init__(self):
        pass
