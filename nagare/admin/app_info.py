# --
# Copyright (c) 2008-2018 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

import pkg_resources

from nagare.admin import command
from nagare.services import reporters


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
            '-l', '--location', action='store_true',
            help='Display the Python package locations'
        )

        parser.add_argument(
            '-m', '--module', action='store_true',
            help='Display the Python modules'
        )

        parser.add_argument(
            '-d', '--description', action='store_true',
            help='Display the plugin description'
        )

    @staticmethod
    def run(on, off, names, application_service, services_service, **columns):
        entry, _ = application_service.load_activated_plugins()[0]
        print 'Application:  %s - %s\n' % (entry.dist.project_name, entry.dist.version)

        activated_columns = {name for name, activated in columns.items() if activated}

        print 'Nagare packages:\n'
        nagare_packages = [(dist,) for dist in pkg_resources.working_set if dist.project_name.startswith('nagare-')]
        reporters.PackagesReporter().report({'package'} | activated_columns, nagare_packages)
        print

        criterias = lambda services, name, _: (name in services) in (on, off)  # noqa: E731

        if names:
            criterias = lambda services, name, service, c=criterias: c(services, name, service) and (name in names)  # noqa: E731

        services_service.report(activated_columns=activated_columns, criterias=criterias)

        return 0
