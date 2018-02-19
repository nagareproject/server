# --
# Copyright (c) 2008-2018 Net-ng.
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
    DESC = 'Launch applications'

    def run(self, publisher_service, services_service):
        # ToDo: files_to_watch
        publisher = publisher_service.service
        return services_service(publisher.serve)

    start = run
