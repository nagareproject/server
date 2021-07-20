# Encoding: utf-8

# --
# Copyright (c) 2008-2021 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from nagare.config import config_from_dict
from nagare.server import services


class Application(services.SelectionService):
    ENTRY_POINTS = 'nagare.applications'
    SELECTOR = 'name'
    CONFIG_SPEC = dict(
        services.SelectionService.CONFIG_SPEC,
        name='string(default=None, help="name of the application entry-point, registered under [nagare.applications]")'
    )
    del CONFIG_SPEC['type']
    LOAD_PRIORITY = 1100

    def __init__(self, name_, dist, name, services_service, **config):
        services_service(super(Application, self).__init__, name_, dist, name, **config)

    @property
    def DESC(self):
        return 'Proxy to the <%s> application' % self.selector

    @classmethod
    def load_plugins(*args, **kw):
        pass

    def create(self):
        global_config = self.plugin_config.pop('_global_config')
        config = {self.SELECTOR: self.selector, self.name: self.plugin_config}

        super(Application, self).load_plugins(self.name, config_from_dict(config), global_config)

        return self.service

    def handle_request(self, chain, app, **params):
        return self.service.handle_request(chain, **params)

    def handle_start(self, app, services_service):
        services_service(self.service.handle_start, app)

    def handle_interaction(self, *args, **params):
        return self.service.handle_interaction(*args, **params)
