# --
# Copyright (c) 2008-2020 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from nagare.services import plugin


class RequestHandlersChain(list):

    def next(self, **params):
        return self.pop()(self, **params)


class Publisher(plugin.Plugin):
    PLUGIN_CATEGORY = 'nagare.publishers'
    CONFIG_SPEC = dict(plugin.Plugin.CONFIG_SPEC, _app_name='string(default=$app_name)')
    has_multi_processes = has_multi_threads = False

    def __init__(self, name, dist, _app_name, **config):
        super(Publisher, self).__init__(name, dist, **config)

        self.app_name = _app_name
        self.request_handlers = []

    def create_app(self, application_service, services_service):
        app = services_service(application_service.create)

        for service in services_service.start_handlers:
            services_service(service.handle_start, app)

        return app

    def _create_app(self, application_service, services_service):
        app = services_service(self.create_app)

        for service in services_service.serve_handlers:
            services_service(service.handle_serve, app)

        return app

    def print_banner(self):
        self.logger.info(self.generate_banner())

    def generate_banner(self):
        return 'Serving application `{}`'.format(self.app_name)

    def start_handle_request(self, app, **params):
        return RequestHandlersChain(self.request_handlers).next(app=app, **params)

    def _serve(self, app):
        self.print_banner()

        return None

    def serve(self, services_service):
        self.request_handlers = [service.handle_request for service in reversed(services_service.request_handlers)]

        app = services_service(self._create_app)
        return services_service(self._serve, app, **self.plugin_config)
