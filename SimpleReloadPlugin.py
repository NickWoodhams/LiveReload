#!/usr/bin/python
# -*- coding: utf-8 -*-

import LiveReload
import sublime_plugin
import os


class SimpleRefresh(LiveReload.Plugin, sublime_plugin.EventListener):

    title = 'Simple Reload'
    description = 'Refresh page, when file is saved'
    file_types = '*'

    def on_post_save(self, view):
        self.refresh(os.path.basename(view.file_name()))
