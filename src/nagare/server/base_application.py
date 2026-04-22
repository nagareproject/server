# --
# Copyright (c) 2014-2025 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

import os

from nagare.services import plugin


class App(plugin.Plugin):
    PLUGIN_CATEGORY = 'nagare.applications'
    CONFIG_SPEC = plugin.Plugin.CONFIG_SPEC | {
        '_root': 'string(default="$root")',
        '_data': 'string(default="$data")',
        '_config_filename': 'string(default="$config_filename")',
        '_user_config_filename': 'string(default="$user_config_filename")',
    }

    def __init__(
        self, name_, dist_, _root, _data, _config_filename, _user_config_filename, reloader_service=None, **config
    ):
        """Initialization."""
        super().__init__(name_, dist_, **config)

        self.version = dist_ and dist_.version
        self.root_path = _root
        self.data_path = _data

        if reloader_service is not None:
            reloader_service.watch_dir(
                dist_.locate_file(''), lambda event, root, filename: True if filename.endswith('.py') else None, True
            )
            reloader_service.watch_file(_config_filename)

            if os.path.isfile(_user_config_filename):
                reloader_service.watch_file(_user_config_filename)

    def handle_start(self, app):
        pass

    def handle_request(self, chain, **kw):
        return None

    def handle_interaction(self):
        return {'app': self}
