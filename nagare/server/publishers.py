# --
# Copyright (c) 2008-2018 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from nagare.services import plugin

from nagare.server import services


class Publisher(plugin.Plugin):
    has_multi_processes = has_multi_threads = False

    def __init__(self, name, dist, **config):
        super(Publisher, self).__init__(name, dist)
        self.config = config

    def create_app(self, application_service, services_service):
        app = services_service(application_service.create)

        for service in services_service.start_handlers.values():
            service.handle_start(app)

        return app

    def serve(self, services_service):
        app = services_service(self.create_app)
        return self._serve(app, **self.config)


class Publishers(services.SelectionService):
    ENTRY_POINTS = 'nagare.publishers'
    LOAD_PRIORITY = 5

    @property
    def DESC(self):
        return 'Proxy to the <%s> publisher' % self.type
