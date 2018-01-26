# --
# Copyright (c) 2008-2018 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

import os
from collections import OrderedDict

from nagare.services import services, plugin


class Services(services.Services):
    ENTRY_POINT = 'nagare.services'

    def merge_initial_config(self, config, **initial_config):
        application_name = config.get('application', {}).get('name', '')
        here = os.path.dirname(config.filename) if config.filename else ''

        super(Services, self).merge_initial_config(
            config,
            application_name=application_name,
            here=here,
            **dict(os.environ, **initial_config)
        )

    @property
    def request_handlers(self):
        return OrderedDict(
            (name, service)
            for name, service in self.items()
            if hasattr(service, 'handle_request')
        )

    @property
    def start_handlers(self):
        return OrderedDict(
            (name, service)
            for name, service in self.items()
            if hasattr(service, 'handle_start')
        )

    def display(self, criterias=lambda services, name, service: True):
        super(Services, self).display(criterias=criterias)
        print

        super(Services, self).display(
            'Request handlers',
            lambda services, name, service: criterias(services, name, service) and hasattr(service, 'handle_request')
        )
        print

        super(Services, self).display(
            'Start handlers',
            lambda services, name, service: criterias(services, name, service) and hasattr(service, 'handle_start')
        )

        return 0


class SelectionService(plugin.SelectionPlugin):
    def __init__(self, name, dist, type, services_service, **config):
        self.services = services_service
        super(SelectionService, self).__init__(name, dist, type, **config)

    def _load_plugin(self, name, dist, plugin, config, *args, **kw):
        return self.services(plugin, name, dist, *args, **dict(config, **kw))

    @property
    def service(self):
        return self.plugin
