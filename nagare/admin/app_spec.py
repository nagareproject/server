# --
# Copyright (c) 2008-2019 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

import collections
from fnmatch import fnmatchcase
from itertools import chain, groupby

from configobj import ConfigObj
from nagare.admin import command


class Spec(command.Command):
    DESC = 'display the services configuration help'

    def set_arguments(self, parser):
        parser.add_argument(
            '-n', '--name', action='append', dest='names',
            help='name of the service to display (can be specified multiple times and wildchars are allowed)'
        )

        super(Spec, self).set_arguments(parser)

    @staticmethod
    def match_service(names, name):
        return any(fnmatchcase(name, pattern) for pattern in (names or ['*']))

    @staticmethod
    def merge_config_specs(services_service):
        return {}

    @classmethod
    def run(cls, names, services_service, application_service=None):
        if application_service is not None:
            services_service(application_service.create)

        config_spec = sorted(
            (name, dict(spec, activated='boolean(default=True)'))
            for name, spec in cls.merge_config_specs(services_service)
            if cls.match_service(names, name)
        )
        if not config_spec:
            print('<empty>')
            return 1

        lines = ConfigObj(collections.OrderedDict(config_spec)).write()
        for section, lines in groupby(lines, lambda l: l.lstrip().startswith('[')):
            lines = chain([''], lines) if section else sorted(lines)
            for line in lines:
                if not line.lstrip().startswith('_'):
                    print(line)

        return 0


class Spec1(Spec):
    WITH_CONFIG_FILENAME = False

    @classmethod
    def merge_config_specs(cls, services_service):
        plugins = cls._create_services(None, None).load_activated_plugins()

        return [(entry.name, plugin.CONFIG_SPEC) for entry, plugin in plugins]


class Spec2(Spec):

    @classmethod
    def merge_config_specs(cls, services_service):
        return [(name, service.plugin_spec) for name, service in services_service.items()]
