# Encoding: utf-8

# --
# Copyright (c) 2008-2019 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from nagare.server import services


class Application(services.SelectionService):
    ENTRY_POINTS = 'nagare.applications'
    CONFIG_SPEC = {'name': 'string(default=None, help="name of the application entry-point, registered under [nagare.applications]")'}
    LOAD_PRIORITY = 1100

    def __init__(self, name_, dist, initial_config, name, services_service, **config):
        services_service(super(Application, self).__init__, name_, dist, initial_config, name)
        self.app_name = name
        self.config = config

    @property
    def DESC(self):
        return 'Proxy to the <%s> application' % self.name

    @property
    def plugin_spec(self):
        if self.plugin is None:
            self.create()

        return super(Application, self).plugin_spec

    @property
    def plugin_config(self):
        if self.plugin is None:
            self.create()

        return super(Application, self).plugin_config

    def _load_plugin(self, name, dist, plugin_cls, initial_config, config, *args, **kw):
        service, config = super(Application, self)._load_plugin(
            name, dist,
            plugin_cls, initial_config, config,
            *args, **kw
        )
        service.plugin_category = 'nagare.applications'

        return service, config

    @staticmethod
    def load_plugins(*args, **kw):
        pass

    def create(self):
        if self.app_name is None:
            self.raise_not_found()

        super(Application, self).load_plugins({self.app_name: self.config})
        return self.service

    def handle_request(self, chain, app, **params):
        return self.service.handle_request(chain, **params)

    def handle_start(self, app, services_service):
        services_service(self.service.handle_start, app)

    def handle_interactive(self, *args, **params):
        return self.service.handle_interactive(*args, **params)
