# --
# Copyright (c) 2008-2021 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from nagare.server import services


class Publishers(services.SelectionService):
    ENTRY_POINTS = 'nagare.publishers'
    CONFIG_SPEC = dict(
        services.SelectionService.CONFIG_SPEC,
        type='string(default=None, help="name of the publisher entry-point, registered under [nagare.publishers]")'
    )
    LOAD_PRIORITY = 20

    @property
    def DESC(self):
        return 'Proxy to the <%s> publisher' % self.type

    def _load_plugin(self, name, dist, plugin_cls, initial_config, config, *args, **kw):
        service = super(Publishers, self)._load_plugin(
            name, dist,
            plugin_cls, initial_config, config,
            *args, **kw
        )

        return service

    def create_app(self, services_service):
        return services_service(self.service.create_app)
