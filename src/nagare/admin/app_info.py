# --
# Copyright (c) 2014-2025 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from fnmatch import fnmatchcase
from itertools import starmap

from nagare.admin import command


class Info(command.Command):
    DESC = 'display application informations'

    def set_arguments(self, parser):
        super().set_arguments(parser)

        parser.add_argument('--on', action='store_true', help='only list the activated services')
        parser.add_argument('--off', action='store_false', help='only list the deactivated services')

        parser.add_argument(
            '-n',
            '--name',
            action='append',
            dest='names',
            help='name of the service to display (can be specified multiple times and wildchars are allowed)',
        )

        parser.add_argument('-v', '--version', action='store_true', help='display the Python package versions')
        parser.add_argument('-l', '--location', action='store_true', help='display the Python package locations')
        parser.add_argument('-m', '--module', action='store_true', help='display the Python modules')
        parser.add_argument('-d', '--description', action='store_true', help='display the plugin description')

    @staticmethod
    def match_service(on, off, names, name, activated):
        if (activated is not None) in (on, off):
            if not names:
                return True

            for pattern in names:
                if len(pattern) != len(name):
                    continue

                if all(starmap(fnmatchcase, zip(name, pattern))):
                    return True

        return False

    @classmethod
    def run(cls, on, off, names, application_service, services_service, **columns):
        config = {application_service.SELECTOR: application_service.selector}
        applications = application_service.iter_entry_points('', application_service.ENTRY_POINTS, config)
        if len(applications) == 1:
            dist, _, _ = applications[0]
            print(f'Application: {dist.name} - version {dist.version}\n')

        names = [name.split('/') for name in (names or [])]
        activated_columns = {name for name, activated in columns.items() if activated}
        services_service.report(
            'services',
            activated_columns,
            lambda entry, fullname, name, plugin_cls, plugin: cls.match_service(on, off, names, fullname, plugin),
        )

        return 0
