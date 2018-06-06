# --
# Copyright (c) 2008-2018 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from fnmatch import fnmatch

from nagare.admin import command


class Info(command.Command):
    DESC = 'information on a service'
    WITH_STARTED_SERVICES = True

    def set_arguments(self, parser):
        parser.add_argument('service_pattern', help='service pattern')

        super(Info, self).set_arguments(parser)

    @staticmethod
    def run(service_pattern, services_service):
        services = [(name, service) for name, service in services_service.items() if fnmatch(name, service_pattern)]

        if not services:
            print 'No service matching <%s>' % service_pattern
            return 1

        for i, (name, service) in enumerate(sorted(services)):
            if i:
                print

            service.info()

        return 0
