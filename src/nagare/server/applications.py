# Encoding: utf-8

# --
# Copyright (c) 2008-2024 Net-ng.
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
        name='string(default=None, help="name of the application entry-point, registered under [nagare.applications]")',
    )
    del CONFIG_SPEC['type']
    LOAD_PRIORITY = 1100

    def __init__(self, name_, dist, name, services_service, **config):
        services_service(super(Application, self).__init__, name, dist, name, **config)

    @property
    def DESC(self):
        return 'Proxy to the <%s> application' % self.selector

    @staticmethod
    def _walk(o, name, entry_points, config, global_config, activated_by_default, get_children):
        if '_initial_config' in config:
            entries = o.iter_entry_points(name, entry_points, config)
            if len(entries) == 1:
                dist, name, entry = entries[0]

                yield (
                    lambda entry, name, cls, plugin, children: (name, cls.CONFIG_SPEC, children),
                    (entry, name, Application, None, []),
                )
        else:
            for e in services.SelectionService._walk(
                o, name, entry_points, config, global_config, activated_by_default, get_children
            ):
                yield e

    @classmethod
    def load_plugins(self, name, config):
        pass

    def create(self):
        config = self.plugin_config.pop('_initial_config')
        global_config = config.pop('_global_config', {})
        config = {self.SELECTOR: self.selector, self.name: config}

        super(Application, self).load_plugins(self.name, config_from_dict(config), global_config, True)

        return self.service

    def handle_request(self, chain, app, **params):
        return self.service.handle_request(chain, **params)

    def handle_start(self, app, services_service):
        services_service(self.service.handle_start, app)

    def handle_interaction(self, *args, **params):
        return self.service.handle_interaction(*args, **params)
