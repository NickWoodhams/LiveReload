#!/usr/bin/python
# -*- coding: utf-8 -*-

import LiveReload
import json
import sublime
try:
  from .Settings import Settings
except ValueError:
  from Settings import Settings

def log(msg):
    print(msg)

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
            log('LiveReload new plugin: ' + cls.__name__)

            # remove old plug-in

            for plugin in cls.plugins:
                if plugin.__name__ == cls.__name__:
                    cls.plugins.remove(plugin)
            cls.plugins.append(cls)

    def togglePlugin(cls, index):

        plugin = cls.plugins[index]()

        if plugin.name in cls.enabled_plugins:
            cls.enabled_plugins.remove(plugin.name)
            sublime.set_timeout(lambda : \
                                sublime.status_message('"%s" the LiveReload plug-in has been disabled!'
                                 % plugin.title), 100)
            plugin.onDisabled()
        else:
            cls.enabled_plugins.append(plugin.name)
            sublime.set_timeout(lambda : \
                                sublime.status_message('"%s" the LiveReload plug-in has been enabled!'
                                 % plugin.title), 100)
            plugin.onEnabled()

        #should only save permanent plug-ins
        p_enabled_plugins =[]
        for p in cls.enabled_plugins:
            log(cls.getPlugin(p).this_session_only)
            if cls.getPlugin(p).this_session_only is not True:
                p_enabled_plugins.append(p)        
        cls.settings.set('enabled_plugins', p_enabled_plugins)

    def getPlugin(cls, className):
        for p in cls.plugins:
            if p.__name__ == className:
                return p()  # instance
        return False

    def listAllDefinedFilters(cls):
        file_types = []
        for plugin in cls.plugins:
            if plugin.__name__ in cls.enabled_plugins:
                if not plugin.file_types is "*":
                    for ext in plugin.file_types.split(','):
                        file_types.append(ext)
        return file_types

    def listPlugins(cls):
        plist = []
        for plugin in cls.plugins:
            p = []
            if plugin.__name__ in cls.enabled_plugins:
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
        log(data, origin)
        for plugin in cls.plugins:
            try:
                plugin().onReceive(data, origin)
            except Exception as e:
                log(e)
        try:
            _wscallback = LiveReload.API.has_callback(data.path)
            if _wscallback:
                try:
                    func = getattr(sys.modules['LiveReload'].Plugin.getPlugin(_wscallback['cls']), _wscallback['name'], None)
                    if func:
                        func(req)
                except Exception as e:
                    log(e)

        except Exception:
            log("no WS handler")


class PluginClass:

    """
    Class for implementing your custom plug-ins, sublime_plugins compatible

    Plug-ins implementing this reference should provide the following attributes:

    - description (string) describing your plug-in
    - title (string) naming your plug-in
    - file_types (string) file_types which should trigger refresh for this plug-in

    """

    @property
    def name(self):
        return str(self.__class__).split('.')[1].rstrip("'>")

    @property
    def isEnabled(self):
        return self.name in self.enabled_plugins

    def should_run(self, filename=False):
        """ Returns True if specified filename is allowed for plug-in, and plug-in itself is enabled """
        all_filters = LiveReload.Plugin.listAllDefinedFilters()
        
        def otherPluginsWithFilter():
            for f in all_filters:
                if filename.endswith(f):
                    return False
            return True

        this_plugin = self.file_types.split(',')

        if [f for f in this_plugin if filename.endswith(f)]:
            log("unique", self.name, filename)
            return True
        elif self.file_types is '*' and otherPluginsWithFilter():
            #no other defined filters and this filter is *
            log("catchall", self.name, filename)
            return True
        else:
            return False

    def addResource(
        self,
        req_path,
        buffer,
        content_type='text/plain',
        ):
        """
        - (string) req_path;  browser path to file you want to serve. Ex: /yourfile.js
        - (string/file) buffer; string or file instance to file you want to serve
        - (string) content_type; Mime-type of file you want to serve
        """

        LiveReload.API.add_static_file(req_path, buffer, content_type)

    def sendCommand(self, command, settings, filename=False):
        """
        - (instance) plug-in; instance
        - (string) command; to trigger in livereload.js (refresh, info, or one of the plugins)
        - (object) settings; additional data that gets passed to command (should be json parsable)
        - (string) original name of file
        """
        if self.isEnabled:
            if command is 'refresh':  # to support new protocol
                settings['command'] = 'reload'
            try:
                if not filename:
                    filename = settings['path'].strip(' ')
            except Exception:
                log("Missing path definition")

            if self.should_run(filename):
                sublime.set_timeout(lambda : sublime.status_message('LiveReload refresh from %s'
                                    % self.name), 100)
                # if we have defined filter
                LiveReload.API.send(json.dumps(settings))
            else:
                log('Skipping ', self.name)
            

    def refresh(self, filename, settings=None):
        """
        Generic refresh command

        - (string) filename; file to refresh (.css, .js, jpg ...)
        - (object) settings; how to reload(entire page or just parts)
        """

        if not settings:
            settings = {
                'path': filename,
                'apply_js_live': self.settings.get('apply_js_live'),
                'apply_css_live': self.settings.get('apply_css_live'),
                'apply_images_live': self.settings.get('apply_images_live'),
                }

        self.sendCommand('refresh', settings)

    def listClients(self):
        """ returns list with all connected clients with their req_url and origin"""
        return LiveReload.API.list_clients()

    def onReceive(self, data, origin):
        """
        Event handler which fires when browser plug-ins sends data
        - (string) data sent by browser
        - (string) origin of data
        """
        pass

    def onEnabled(self):
        """ Runs when plug-in is enabled via menu"""
        pass

    def onDisabled(self):
        """ Runs when plug-in is disabled via menu"""
        pass

    @property
    def this_session_only(self):
        """ Should it stay enabled forever or this session only """
        return False

    @property
    def file_types(self):
        """ Run plug-in only with this file extensions, defaults to all extensions"""
        return '*'

##black magic, python2 vs python3
try:
    PluginInterface = PluginFactory('PluginInterface', (object,PluginClass, ), {})
except TypeError:
    PluginInterface = PluginFactory('PluginInterface', (PluginClass, ), {})