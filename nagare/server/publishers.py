# --
# Copyright (c) 2008-2019 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from nagare.server import services


class Publishers(services.SelectionService):
    ENTRY_POINTS = 'nagare.publishers'
    CONFIG_SPEC = {'type': 'string(default=None help="name of the publisher entry-point, registered under [nagare.publishers]")'}
    LOAD_PRIORITY = 20

    def _load_plugin(self, name, dist, plugin_cls, initial_config, config, *args, **kw):
        service, config = super(Publishers, self)._load_plugin(
            name, dist,
            plugin_cls, initial_config, config,
            *args, **kw
        )
        service.plugin_category = 'nagare.publishers'

        return service, config

    def create_app(self, services_service):
        return services_service(self.service.create_app)

    @property
    def DESC(self):
        return 'Proxy to the <%s> publisher' % self.type
