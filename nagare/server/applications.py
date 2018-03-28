# Encoding: utf-8

# --
# Copyright (c) 2008-2018 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from nagare.server import services


class Application(services.SelectionService):
    ENTRY_POINTS = 'nagare.applications'
    CONFIG_SPEC = {'name': 'string(default=None)'}
    LOAD_PRIORITY = 1100

    def __init__(self, name_, dist, initial_config, name, services_service, **config):
        services_service(super(Application, self).__init__, name, dist, initial_config, name)
        self.config = config

    @property
    def DESC(self):
        return 'Proxy to the <%s> application' % self.name

    def load_plugins(*args, **kw):
        pass

    def create(self):
        super(Application, self).load_plugins({self.name: self.config})
        return self.service

    def handle_request(self, chain, app, **params):
        return self.service.handle_request(chain, **params)

    def handle_start(self, app):
        self.service.handle_start()

    def handle_interactive(self, *args, **params):
        return self.service.handle_interactive(*args, **params)
