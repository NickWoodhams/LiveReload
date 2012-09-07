#!/usr/bin/python
# -*- coding: utf-8 -*-

import LiveReload
import json
import sublime
from Settings import Settings


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
            cls.settings = Settings()
            cls.plugins = []
            cls.enabled_plugins = cls.settings.get('enabled_plugins', [])
        else:
            print 'LiveReload new plugin: ' + cls.__name__

            # remove old plugin

            for plugin in cls.plugins:
                if plugin.__name__ == cls.__name__:
                    cls.plugins.remove(plugin)
            cls.plugins.append(cls)

    def togglePlugin(cls, index):

        plugin = cls.plugins[index]()

        if plugin.name in cls.enabled_plugins:
            cls.enabled_plugins.remove(plugin.name)
            sublime.set_timeout(lambda : \
                                sublime.status_message('"%s" the LiveReload plugin has been disabled!'
                                 % plugin.title), 100)
            plugin.onDisabled()
        else:
            cls.enabled_plugins.append(plugin.name)
            sublime.set_timeout(lambda : \
                                sublime.status_message('"%s" the LiveReload plugin has been enabled!'
                                 % plugin.title), 100)
            plugin.onEnabled()

        if plugin.this_session_only is not True:
            print 'LiveReload enablig plugin forever: ' + plugin.name
            cls.settings.set('enabled_plugins', cls.enabled_plugins)

    def getPlugin(cls, className):
        for p in cls.plugins:
            print 'p name %s' % p.__name__
            if p.__name__ == className:
                print 'Found ' + className
                return p()  # instance
        return False

    def listPlugins(cls):
        plist = []
        for plugin in cls.plugins:
            p = []
            if plugin.__name__ == cls.enabled_plugins:
                p.append('Disable - ' + str(plugin.title))
            else:
                if plugin.this_session_only is not True:
                    p.append('Enable - ' + str(plugin.title))
                else:
                    p.append('Enable - ' + str(plugin.title) + ' (this session)')
            if plugin.description:
                p.append(str(plugin.description) + ' (' + str(plugin.file_types) + ')')
            plist.append(p)
        return plist

    def dispatch_OnReceive(cls, data, origin):
        for plugin in cls.plugins:
            try:
                plugin().onReceive(data, origin)
            except Exception, e:
                print e


class PluginClass:

    """
    Class for implementing your custom plugins, sublime_plugins compatible

    Plugins implementing this reference should provide the following attributes:

    description (string) describing your plugin
    title (string) naming your plugin
    file_types (string) file_types which should trigger refresh for this plugin

    Public methods:

    self.refresh(filename, settings):

        (string) filename; file to refresh (.css, .js, jpg ...)
        (object) settings; how to reload(entire page or just parts)

    self.sendCommand(plugin, command, settings):

        (instance) plugin; instance
        (string) command; to trigger in livereload.js (refresh, info, or one of the plugins)
        (object) settings; additional data that gets passed to command (should be json parsable)

    self.addResource(req_path, buffer, content_type='text/plain'):

        (string) req_path;  browser path to file you want to serve. Ex: /yourfile.js
        (string/file) buffer; string or file instance to file you want to serve
        (string) content_type; Mime-type of file you want to serve

    self.listClients():

        returns list with all connected clients with their req_url and origin

    self.onReceive():

        Event handler which fires when browser plugins sends data
        (string) data sent by browser
        (string) origin of data
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
            sublime.set_timeout(lambda : sublime.status_message('LiveReload refresh from %s'
                                % self.name), 100)
            if command is 'refresh':  # to support new protocoil
                settings['command'] = 'reload'

            LiveReload.API.send(json.dumps(settings))

    def refresh(self, filename, settings=None):

        if not settings:
            settings = {
                'path': filename,
                'apply_js_live': self.settings.get('apply_js_live'),
                'apply_css_live': self.settings.get('apply_css_live'),
                'apply_images_live': self.settings.get('apply_images_live'),
                }

        if [f for f in self.file_types.split(',') if filename.strip(' ').endswith(f)]:

            # if we have defined filter

            self.sendCommand('refresh', settings)
        elif self.file_types is '*':

            # for everything else

            self.sendCommand('refresh', settings)
        else:
            print 'Missing file_types filter in %s plug-in implementation' % self.name

    def listClients(self):
        return LiveReload.API.list_clients()

    def onReceive(self, data, origin):
        pass

    def onEnabled(self):
        pass

    def onDisabled(self):
        pass

    @property
    def this_session_only(self):
        return False

    @property
    def file_types(self):
        return '*'
