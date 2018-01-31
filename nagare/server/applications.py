# Encoding: utf-8

# --
# Copyright (c) 2008-2018 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from .services import SelectionService


class Application(SelectionService):
    ENTRY_POINTS = 'nagare.applications'
    CONFIG_SPEC = {'name': 'string(default=None)'}
    LOAD_PRIORITY = 2000

    def __init__(self, name_, dist, name, services_service, **config):
        services_service(super(Application, self).__init__, name_, dist, name)

        self.name = name
        self.config = config

    @property
    def DESC(self):
        return 'Proxy to the <%s> application' % self.name

    def load_plugins(*args, **config):
        pass

    def create(self):
        super(Application, self).load_plugins({self.name: self.config})
        return self.service

    def handle_start(self, *args, **kw):
        if self.service is not None:
            self.service.handle_start(*args, **kw)

    def handle_request(self, *args, **kw):
        return self.service.handle_request(*args, **kw)

    def handle_interactive(self, *args, **kw):
        return self.service.handle_interactive(*args, **kw)
