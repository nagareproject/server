# --
# Copyright (c) 2008-2018 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from nagare.admin import command


class Info(command.Command):
    DESC = 'information on an applications'

    def set_arguments(self, parser):
        super(Info, self).set_arguments(parser)

        parser.add_argument(
            '--on', action='store_true',
            help='only list the activated services'
        )

        parser.add_argument(
            '--off', action='store_false',
            help='only list the deactivated services'
        )

        parser.add_argument(
            '-n', '--name', action='append', dest='names',
            help='name of the service to display (can be specified multiple times)'
        )

    def run(self, on, off, names, services_service):
        criterias = lambda services, name, _: (name in services) in (on, off)  # noqa: E731

        if names:
            criterias = lambda services, name, service, c=criterias: c(services, name, service) and (name in names)  # noqa: E731

        services_service.display(criterias=criterias)
        return 0
