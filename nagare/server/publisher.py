# --
# Copyright (c) 2008-2018 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

import os

from nagare.services import plugin


class RequestHandlersChain(list):

    def next(self, **params):
        return self.pop()(self, **params)


class Publisher(plugin.Plugin):
    has_multi_processes = has_multi_threads = False

    def __init__(self, name, dist, **config):
        super(Publisher, self).__init__(name, dist)

        self.config = config
        self.request_handlers = []

    @staticmethod
    def monitor(reloader, reload_action):
        return reloader.monitor(reload_action) if reloader is not None else 0

    @staticmethod
    def create_app(application_service, services_service):
        app = services_service(application_service.create)

        for service in services_service.start_handlers:
            service.handle_start(app)

        return app

    _create_app = create_app

    def start_handle_request(self, app, **params):
        return RequestHandlersChain(self.request_handlers).next(app=app, **params)

    def _serve(self, app, **params):
        raise NotImplementedError()

    def serve(self, reloader_service=None, services_service=None, **params):
        status = self.monitor(reloader_service, lambda reloader, path: os._exit(3))
        if status == 0:
            self.request_handlers = [service.handle_request for service in reversed(services_service.request_handlers)]
            app = services_service(self._create_app)

            status = services_service(self._serve, app, **dict(self.config, **params))

        return status
