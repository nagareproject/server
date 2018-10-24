# --
# Copyright (c) 2008-2018 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from fnmatch import fnmatchcase

from nagare.admin import command


class Config(command.Command):
    DESC = 'services configuration'
    WITH_STARTED_SERVICES = True

    def set_arguments(self, parser):
        parser.add_argument(
            '-n', '--name', action='append', dest='names',
            help='name of the service to display (can be specified multiple times and wildchars are allowed)'
        )

        super(Config, self).set_arguments(parser)

    @staticmethod
    def match_service(names, name):
        return any(fnmatchcase(name, pattern) for pattern in (names or ['*']))

    @classmethod
    def run(cls, names, services_service):
        services = [(name, service) for name, service in services_service.items() if cls.match_service(names, name)]

        if not services:
            print('<empty>')
            return 1

        for i, (name, service) in enumerate(sorted(services)):
            service.info()

        return 0
