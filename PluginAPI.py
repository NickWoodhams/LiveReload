#!/usr/bin/python
# -*- coding: utf-8 -*-

import LiveReload
import json
import sublime


class PluginFactory(type):

    """
    Based on example from http://martyalchin.com/2008/jan/10/simple-plugin-framework/
    """

    def __init__(
        cls,
        name,
        bases,
        attrs,
        ):

        if not hasattr(cls, 'plugins'):
            cls.settings = \
                sublime.load_settings('LiveReload.sublime-settings')
            cls.plugins = []
            cls.enabled_plugins = cls.settings.get('enabled_plugins',
                    [])
        else:
            print 'LiveReload new plugin: ' + cls.__name__

            # remove old plugin

            for plugin in cls.plugins:
                if plugin.__name__ == cls.__name__:
                    cls.plugins.remove(plugin)
            cls.plugins.append(cls)

    def togglePlugin(cls, index):
        plugin = cls.plugins[index]
        if plugin.__name__ in cls.enabled_plugins:
            cls.enabled_plugins.remove(plugin.__name__)
            sublime.set_timeout(lambda : \
                                sublime.status_message('%s the LiveReload plugin has been disabled!'
                                 % plugin.title), 100)
        else:
            cls.enabled_plugins.append(plugin.__name__)
            sublime.set_timeout(lambda : \
                                sublime.status_message('%s the LiveReload plugin has been enabled!'
                                 % plugin.title), 100)
        cls.settings = \
            sublime.load_settings('LiveReload.sublime-settings')
        cls.settings.set('enabled_plugins', cls.enabled_plugins)
        sublime.save_settings('LiveReload.sublime-settings')

    def listPlugins(cls):
        plist = []
        for plugin in cls.plugins:
            p = []
            if plugin.__name__ in cls.enabled_plugins:
                p.append('Disable - ' + str(plugin.title))
            else:
                p.append('Enable - ' + str(plugin.title))
            if plugin.description:
                p.append(str(plugin.description) + ' ('
                         + str(plugin.file_types) + ')')
            plist.append(p)
        return plist

    def __get__(cls, instance, owner):
        return [p(instance) for p in cls.plugins]


class PluginClass:

    """
    Class for implementing your custom plugins, sublime_plugins compatible

    Plugins implementing this reference should provide the following attributes:

    description (string) describing your plugin
    title (string) naming your plugin

    Public methods:

    self.refresh(filename, settings):

        (string) filename; file to refresh (.css, .js, jpg ...)
        (object) settings; how to reload(entire page or just parts)

    self.sendCommand(plugin, command, settings):

        In conjustion with addResourceCan be used to write custom plugins

        (instance) plugin; instance
        (string) command; to trigger in livereload.js (refresh,info, or one of the plugins)
        (object) settings; additiona data that gets paseed to command (should be json parsable)

    self.addResource(req_path, buffer, content_type='text/plain'):

        (string) req_path;  browser path to file you want to serve. Ex: /yourfile.js
        (string/file) buffer; string or file instance to file you want to serve
        (string) content_type; Mime-type of file you want to serve

    """

    __metaclass__ = PluginFactory

    @property
    def name(self):
        return str(self.__class__).split('.')[1].rstrip("'>")

    @property
    def isEnabled(self):
        return self.name in self.enabled_plugins

    def addResource(
        self,
        req_path,
        buffer,
        content_type='text/plain',
        ):

        LiveReload.API.add_static_file(req_path, buffer, content_type)

    def sendCommand(self, command, settings):

        if self.isEnabled:
            sublime.set_timeout(lambda : \
                                sublime.status_message('LiveReload refresh from %s'
                                 % self.name), 100)
            LiveReload.API.send(json.dumps([command, settings]))

    def refresh(self, filename, settings=None):
        if self.file_types is '*' or [f for f in
                self.file_types.split(',') if filename.strip(' '
                ).endswith(f)]:
            if not settings:
                settings = {
                    'path': filename,
                    'apply_js_live': self.settings.get('apply_js_live'
                            ),
                    'apply_css_live': self.settings.get('apply_css_live'
                            ),
                    'apply_images_live': self.settings.get('apply_images_live'
                            ),
                    }

            self.sendCommand('refresh', settings)
