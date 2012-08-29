#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import threading
import subprocess
import sys
import sublime
import sublime_plugin

# fix for import order

sys.path.append(os.path.join(sublime.packages_path(), 'LiveReload'))
LiveReload = __import__('LiveReload')
sys.path.remove(os.path.join(sublime.packages_path(), 'LiveReload'))


class CompassThread(threading.Thread):

    def __init__(
        self,
        dirname,
        filename,
        on_compile,
        ):

        self.dirname = dirname
        self.filename = filename
        self.stdout = None
        self.stderr = None
        self.on_compile = on_compile
        threading.Thread.__init__(self)

    def run(self):
        global LivereloadFactory
        p = subprocess.Popen(['compass', 'compile', self.dirname], shell=True,
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        if p.stdout.read():
            self.on_compile()


class CompassPreprocessor(LiveReload.Plugin, sublime_plugin.EventListener):

    title = 'Compass Preprocessor'
    description = 'Compile and refresh page, when file is compiled'
    file_types = '.scss'
    this_session_only = True

    def on_post_save(self, view):
        if view.file_name().find('.scss') > 0 and bool(self.settings.get('compass_css_dir')):
            filename = view.file_name().replace('sass', self.settings.get('compass_css_dir'
                                                )).replace('.scss', '.css')
            dirname = os.path.dirname(os.path.dirname(filename))
            compiler = CompassThread(dirname, filename, self.on_compile)
            compiler.start()

    def on_compile(self):
        self.refresh(os.path.basename(view.file_name()))
