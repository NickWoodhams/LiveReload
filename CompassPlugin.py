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
        p = subprocess.Popen(['compass compile ' + self.dirname.replace('\\', '/')], shell=True,
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        if p.stdout.read():
            self.on_compile()


class CompassPreprocessor(LiveReload.Plugin, sublime_plugin.EventListener):

    title = 'Compass Preprocessor'
    description = 'Compile and refresh page, when file is compiled'
    file_types = '.scss,.sass'
    this_session_only = True
    file_name = ''

    def on_post_save(self, view):
        if view.file_name().endswith('.scss') or view.file_name().endswith('.sass'):
            file_name = view.file_name().replace('.scss','.css').replace('.sass','.css')
            self.file_name = os.path.basename(file_name);
            dirname = os.path.dirname(view.file_name())
            cfg_file = os.path.join(dirname, "config.rb")

            # autocreate config.rb if no config.rb detected
            if not os.path.exists(cfg_file):
                print "Generating config.rb"

                config_rb = """http_path = "/"
                css_dir = "."
                sass_dir = "."
                images_dir = "img"
                javascripts_dir = "javascripts"
                output_style = :nested
                relative_assets=true
                line_comments = false
                """
                
                with open('file_to_write', 'w') as f:
                            f.write(config_rb)

            compiler = CompassThread(dirname, file_name, self.on_compile)
            compiler.start()

    def on_compile(self):
        settings = {
            'path': self.file_name,
            'apply_js_live': False,
            'apply_css_live': True,
            'apply_images_live': True,
        }
        self.sendCommand('refresh', settings)
