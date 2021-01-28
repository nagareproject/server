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

import os
import random

from nagare.admin import command


class Serve(command.Command):
    DESC = 'launch an application'

    @staticmethod
    def monitor(reload_action, services_service, reloader_service=None):
        if reloader_service is None:
            status = 0
        else:
            status = services_service(reloader_service.monitor, reload_action)

        return status

    def run(self, publisher_service, services_service):
        random.seed()

        status = services_service(self.monitor, lambda reloader, path: os._exit(3))
        if status == 0:
            publisher = publisher_service.service
            status = services_service(publisher.serve)

        return status
