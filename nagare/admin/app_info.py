# --
# Copyright (c) 2008-2021 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from fnmatch import fnmatchcase

from nagare.admin import command


class Info(command.Command):
    DESC = 'display application informations'

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
            help='name of the service to display (can be specified multiple times and wildchars are allowed)'
        )

        parser.add_argument(
            '-v', '--version', action='store_true',
            help='display the Python package versions'
        )

        parser.add_argument(
            '-l', '--location', action='store_true',
            help='display the Python package locations'
        )

        parser.add_argument(
            '-m', '--module', action='store_true',
            help='display the Python modules'
        )

        parser.add_argument(
            '-d', '--description', action='store_true',
            help='display the plugin description'
        )

    @staticmethod
    def match_service(on, off, names, services, name):
        matches = [fnmatchcase(name, pattern) for pattern in (names or ['*'])]

        return ((name in services) in (on, off)) and any(matches)

    @classmethod
    def run(cls, on, off, names, application_service, services_service, **columns):
        application = application_service.load_activated_plugins()
        if len(application):
            entry, _ = application[0]
            print('Application:  %s - %s\n' % (entry.dist.project_name, entry.dist.version))

        activated_columns = {name for name, activated in columns.items() if activated}

        services_service.report(
            activated_columns=activated_columns,
            criterias=lambda services, name, _: cls.match_service(on, off, names, services, name)
        )

        return 0
