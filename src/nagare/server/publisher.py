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


class Publisher(plugin.Plugin):
    PLUGIN_CATEGORY = 'nagare.publishers'
    CONFIG_SPEC = plugin.Plugin.CONFIG_SPEC | {'app_name': 'string(default="$app_name")'}
    has_multi_processes = has_multi_threads = False

    def __init__(self, name, dist, _app_name, **config):
        super().__init__(name, dist, **config)

        self.app_name = _app_name
        self.request_handlers = []

    @staticmethod
    def monitor(reload_action, services_service, reloader_service=None):
        if reloader_service is None:
            status = 0
        else:
            status = services_service(reloader_service.monitor, reload_action)

        return status

    def create_app(self, application_service, services_service):
        app = services_service(application_service.create)
        services_service.handle_start(app, services_service)

        return app

    def _create_app(self, application_service, services_service):
        app = services_service(self.create_app)
        services_service.handle_serve(app)

        return app

    def print_banner(self):
        self.logger.info(self.generate_banner())

    def generate_banner(self):
        return f'Serving application `{self.app_name}`'

    def handle_request(self, app, services_service, **params):
        return services_service.handle_request([], app=app, **params)

    start_handle_request = handle_request

    def _serve(self, app, **params):
        self.print_banner()

        return None

    def serve(self, services_service, reloader_service=None, **params):
        status = services_service(self.monitor, lambda reloader, path: os._exit(3))
        if status == 0:
            app = services_service(self._create_app)
            status = services_service(self._serve, app, **(self.plugin_config | params))

        return status
