# --
# Copyright (c) 2008-2020 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from fnmatch import fnmatchcase
from collections import OrderedDict
from itertools import chain, groupby

from configobj import ConfigObj

from nagare.services.config import Validator

from nagare.admin import command


class Config(command.Command):
    DESC = 'display the services configuration and extra informations'

    def set_arguments(self, parser):
        parser.add_argument(
            '-n', '--name', action='append', dest='names',
            help='name of the service to display (can be specified multiple times and wildchars are allowed)'
        )

        parser.add_argument(
            '-c', '--config', action='store_false', dest='with_info',
            help='only display the configuration'
        )

        parser.add_argument(
            '-i', '--info', action='store_false', dest='with_config',
            help='only display the extra informations'
        )

        parser.add_argument(
            '--not-modified', action='store_true',
            help='display the not modified configuration parameters (parameters with default value)'
        )

        parser.add_argument(
            '--modified', action='store_true',
            help='display the modified configuration parameters'
        )

        super(Config, self).set_arguments(parser)

    @staticmethod
    def match_service(names, name):
        return any(fnmatchcase(name, pattern) for pattern in (names or ['*']))

    @classmethod
    def compare(cls, validator, spec, config, not_modified, modified):
        r = {}
        for k, v in config.items():
            check = spec.get(k)
            if check is None:
                if modified:
                    r[k] = v
                continue

            if isinstance(v, dict):
                v = cls.compare(validator, check, v, not_modified, modified)
                if v:
                    r[k] = v
            else:
                try:
                    default = validator.get_default_value(check)
                except KeyError:
                    continue

                if (modified and (v != default)) or (not_modified and (v == default)):
                    r[k] = v

        return r

    @classmethod
    def run(cls, names, with_config, with_info, not_modified, modified, application_service, services_service):
        services_service(application_service.create)

        services = sorted((name, service) for name, service in services_service.items() if cls.match_service(names, name))
        if not services:
            print('<empty>')
            return 1

        config = OrderedDict((name, dict(service.plugin_config, activated=True)) for name, service in services)

        if with_config:
            print('Configuration')
            print('-------------')

            if not_modified or modified:
                spec = {name: dict(service.plugin_spec, activated='boolean(default=True)') for name, service in services}
                config = cls.compare(Validator(), spec, config, not_modified, modified)

            lines = ConfigObj(config).write()

            for section, lines in groupby(lines, lambda l: l.lstrip().startswith('[')):
                lines = chain([''], lines) if section else sorted(lines)
                for line in lines:
                    if not line.lstrip().startswith('_'):
                        print(line)

        if with_info:
            for name, service in services:
                info = '\n'.join(service.format_info())
                if not info:
                    continue

                print('')
                title = "Service '{}'".format(name)
                print(title)
                print('-' * len(title))
                print('')

                print(info)

        return 0
