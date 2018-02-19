# Encoding: utf-8

# --
# Copyright (c) 2008-2018 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from nagare.services import plugin


class App(plugin.Plugin):
    CONFIG_SPEC = {'root': 'string(default="$root_path")', 'data': 'string(default="$data_path")'}

    def __init__(self, name, dist, root, data):
        """Initialization
        """
        super(App, self).__init__(name, dist)

        self.version = dist and dist.version
        self.root_path = root
        self.data_path = data

    def handle_request(self, chain, **kw):
        return None

    def handle_interactive(self):
        return {'app': self}
