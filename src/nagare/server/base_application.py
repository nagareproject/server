# Encoding: utf-8

# --
# Copyright (c) 2008-2023 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

import os
import sys

from nagare.services import plugin


class App(plugin.Plugin):
    PLUGIN_CATEGORY = 'nagare.applications'
    CONFIG_SPEC = dict(
        plugin.Plugin.CONFIG_SPEC,
        _root='string(default="$root")',
        _data='string(default="$data")',
        _config_filename='string(default="$config_filename")',
        _user_config_filename='string(default="$user_config_filename")',
    )

    def __init__(
        self, name, dist, _root, _data, _config_filename, _user_config_filename, reloader_service=None, **config
    ):
        """Initialization."""
        super(App, self).__init__(name, dist, **config)

        self.version = dist and dist.version
        self.root_path = _root
        self.data_path = _data

        if reloader_service is not None:
            for module in list(sys.modules.values()):
                filename = getattr(module, '__file__', None)
                if filename and ('lib/python' not in filename.lower()):
                    filename = os.path.abspath(filename)
                    reloader_service.watch_file(filename[:-1] if filename.endswith(('.pyc', '.pyo')) else filename)

            reloader_service.watch_file(_config_filename)
            if os.path.isfile(_user_config_filename):
                reloader_service.watch_file(_user_config_filename)

    def handle_start(self, app):
        pass

    def handle_request(self, chain, **kw):
        return None

    def handle_interaction(self):
        return {'app': self}
