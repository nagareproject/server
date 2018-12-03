# Encoding: utf-8

# --
# Copyright (c) 2008-2018 Net-ng.
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
    CONFIG_SPEC = {
        'root': 'string(default="$root_path")',
        'data': 'string(default="$data_path")',
        '_config_filename': 'string(default=$config_filename)',
        '_user_config_filename': 'string(default=$user_config_filename)'
    }

    def __init__(
        self,
        name, dist,
        root, data,
        _config_filename, _user_config_filename,
        reloader_service=None
    ):
        """Initialization
        """
        super(App, self).__init__(name, dist)

        self.version = dist and dist.version
        self.root_path = root
        self.data_path = data

        if reloader_service is not None:
            for module in sys.modules.values():
                filename = getattr(module, '__file__', None)
                if filename and ('lib/python' not in filename.lower()):
                    filename = os.path.abspath(filename)
                    reloader_service.watch_file(filename[:-1] if filename.endswith(('.pyc', '.pyo')) else filename)

            reloader_service.watch_file(_config_filename)
            reloader_service.watch_file(_user_config_filename)

    def handle_start(self):
        pass

    def handle_request(self, chain, **kw):
        return None

    def handle_interactive(self):
        return {'app': self}
