# --
# Copyright (c) 2008-2018 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from nagare.services import services, plugin


class Services(services.Services):
    ENTRY_POINT = 'nagare.services'

    def handlers(self, attribute):
        return [service for service in self.values() if hasattr(service, attribute)]

    @property
    def request_handlers(self):
        return self.handlers('handle_request')

    @property
    def start_handlers(self):
        return self.handlers('handle_start')

    @property
    def interactive_handlers(self):
        return self.handlers('handle_interactive')

    def report(self, activated_columns=None, criterias=lambda services, name, service: True):
        super(Services, self).report(activated_columns=activated_columns, criterias=criterias)
        print('')

        super(Services, self).report(
            'Request handlers',
            activated_columns,
            lambda services, name, service: criterias(services, name, service) and hasattr(service, 'handle_request')
        )
        print('')

        super(Services, self).report(
            'Start handlers',
            activated_columns,
            lambda services, name, service: criterias(services, name, service) and hasattr(service, 'handle_start')
        )

        return 0


class SelectionService(plugin.SelectionPlugin):

    def __init__(self, name, dist, initial_config, type, services_service, **config):
        self.initial_config = initial_config
        self.services = services_service

        super(SelectionService, self).__init__(name, dist, type, **config)

    def load_plugins(self, config, config_section=None, **initial_config):
        initial_config.update(self.initial_config)

        super(SelectionService, self).load_plugins(config, config_section, **initial_config)

    def _load_plugin(self, name, dist, plugin_cls, initial_config, config, *args, **kw):
        config = dict(config, **kw)
        service = self.services(plugin_cls, name, dist, **config)

        return service, config

    @property
    def service(self):
        return self.plugin
