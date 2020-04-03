# --
# Copyright (c) 2008-2020 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

"""The ``serve`` administrative command
"""

from nagare.admin import command


class Serve(command.Command):
    DESC = 'launch an application'

    def run(self, publisher_service, services_service, **kw):
        publisher = publisher_service.service
        return services_service(publisher.serve, **kw)
