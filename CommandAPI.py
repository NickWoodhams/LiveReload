#!/usr/bin/python
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
import LiveReload


class LiveReloadSendCommand(sublime_plugin.ApplicationCommand):

    def run(self, data):
        LiveReload.API.send(data)

    def is_visible(self):
        return False


class LiveReloadAddJSCommand(sublime_plugin.ApplicationCommand):

    def run(self, source, order):
        pass

    def is_visible(self):
        return False


class LiveReloadAddResCommand(sublime_plugin.ApplicationCommand):

    def run(
        self,
        buffer,
        path,
        content_type,
        ):

        pass

    def is_visible(self):
        return False


class LiveReloadHelp(sublime_plugin.ApplicationCommand):

    def run(self):
        pass


class LiveReloadEnablePluginCommand(sublime_plugin.ApplicationCommand):

    def on_done(self, index):
        if not index is -1:
            LiveReload.Plugin.togglePlugin(index)

    def run(self):

        sublime.active_window().show_quick_panel(LiveReload.Plugin.listPlugins(),
                self.on_done)
