#!/usr/bin/python
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
import LiveReload


class LiveReloadHelp(sublime_plugin.ApplicationCommand):

    def run(self):
        pass


class LiveReloadEnablePluginCommand(sublime_plugin.ApplicationCommand):

    def on_done(self, index):
        if not index is -1:
            LiveReload.Plugin.togglePlugin(index)

    def run(self):
        print(dir(LiveReload.Plugin))
        sublime.active_window().show_quick_panel(LiveReload.Plugin.listPlugins(), self.on_done)
