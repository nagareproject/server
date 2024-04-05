# --
# Copyright (c) 2008-2024 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from functools import reduce

from nagare.services import plugin, services


class RequestHandlersChain(list):
    def next(self, **params):
        return self.pop()(self, **params)


class Services(services.Services):
    def __init__(self, *args, **kw):
        super(Services, self).__init__(*args, **kw)
        self.request_handlers = None

    @staticmethod
    def _has_handler(service, handle_name):
        return getattr(service, 'has_{}_handler'.format(handle_name), hasattr(service, 'handle_{}'.format(handle_name)))

    def handlers(self, handle_name):
        return [service for service in self.values() if self._has_handler(service, handle_name)]

    def has_handler(self, handle_name):
        return bool(self.handlers(handle_name))

    @property
    def has_serve_handler(self):
        return self.has_handler('serve')

    @property
    def has_start_handler(self):
        return self.has_handler('start')

    @property
    def has_request_handler(self):
        return self.has_handler('request')

    @property
    def has_reload_handler(self):
        return self.has_handler('reload')

    @property
    def has_interaction_handler(self):
        return self.has_handler('interaction')

    # -----------------------------------------------------------------------------------------------------------------

    def handle_serve(self, app):
        for service in self.handlers('serve'):
            self(service.handle_serve, app)

    def handle_start(self, app, services_service):
        for service in self.handlers('start'):
            (services_service or self)(service.handle_start, app)

    def create_request_handlers_chain(self, chain):
        if self.request_handlers is None:
            self.request_handlers = [service.handle_request for service in reversed(self.handlers('request'))]

        return chain + self.request_handlers

    def handle_request(self, chain, **params):
        return RequestHandlersChain(self.create_request_handlers_chain(chain)).next(**params)

    def handle_reload(self):
        for service in self.handlers('reload'):
            service.handle_reload()

    def handle_interaction(self):
        namespaces = [service.handle_interaction() for service in self.handlers('interaction')]
        return reduce(lambda d, new: dict(d, **new), namespaces, {})

    # -----------------------------------------------------------------------------------------------------------------

    def report(self, name, activated_columns=None, criterias=lambda *args: True):
        super(Services, self).report(name, 'Services', activated_columns, criterias)

        print('')

        super(Services, self).report(
            name,
            'Request handlers',
            activated_columns,
            lambda *args: criterias(*args) and self._has_handler(args[-1], 'request'),
        )

        print('')

        super(Services, self).report(
            name,
            'Start handlers',
            activated_columns,
            lambda *args: criterias(*args) and self._has_handler(args[-1], 'start'),
        )

        return 0


class SelectionService(plugin.SelectionPlugin):
    def __init__(self, name_, dist, type, services_service, **config):
        self.services = services_service
        super(SelectionService, self).__init__(type, dist, type, **config)

    def _load_plugin(self, name_, dist, plugin_cls, **config):
        config = config.copy()
        del config[self.SELECTOR]

        return self.services(plugin_cls, name_, dist, **config)

    @property
    def service(self):
        return self.plugin


class NagareServices(Services):
    ENTRY_POINTS = 'nagare.services'
