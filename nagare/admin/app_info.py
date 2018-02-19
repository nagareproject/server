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

        parser.add_argument(
            '-p', '--package', action='store_true',
            help='Display the Python packages'
        )

        parser.add_argument(
            '-v', '--version', action='store_true',
            help='Display the Python package versions'
        )

        parser.add_argument(
            '-m', '--module', action='store_true',
            help='Display the Python modules'
        )

        parser.add_argument(
            '-l', '--location', action='store_true',
            help='Display the Python package locations'
        )

        parser.add_argument(
            '-d', '--description', action='store_true',
            help='Display the plugin description'
        )

    @staticmethod
    def run(on, off, names, services_service, **columns):
        activated_columns = {name for name, activated in columns.items() if activated}

        criterias = lambda services, name, _: (name in services) in (on, off)  # noqa: E731

        if names:
            criterias = lambda services, name, service, c=criterias: c(services, name, service) and (name in names)  # noqa: E731

        services_service.display(activated_columns=activated_columns, criterias=criterias)
        return 0
