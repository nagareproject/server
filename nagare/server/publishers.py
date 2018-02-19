# --
# Copyright (c) 2008-2018 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from nagare.server import services


class Publishers(services.SelectionService):
    ENTRY_POINTS = 'nagare.publishers'
    LOAD_PRIORITY = 20

    def create_app(self, services_service):
        return services_service(self.service.create_app)

    @property
    def DESC(self):
        return 'Proxy to the <%s> publisher' % self.type
