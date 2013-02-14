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
class SimpleWSCallback(LiveReload.Plugin):

    title = 'Simple Reload from websocket request'
    description = \
        'Refresh page with liverelaod.plugins.SimpleWSCallback.on_post_compile(object)'
    file_types = '*'
    this_session_only = True

    @LiveReload.websocket_callback
    def on_post_compile(self, req):
        print 'on_post_compile', req
        self.refresh(os.path.basename(sublime.active_window().active_view().file_name()))
        return 'All ok from SimpleRefreshCallBack!'
