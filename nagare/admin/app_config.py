# --
# Copyright (c) 2008-2021 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from itertools import starmap
from fnmatch import fnmatchcase

from nagare.admin import command
from nagare.config import config_from_dict


class Config(command.Command):
    DESC = 'display the services configuration and extra informations'

    def __init__(self, name=None, dist=None, **config):
        super(Config, self).__init__(name, dist, **config)
        self.raw_config = None

    def set_arguments(self, parser):
        parser.add_argument(
            '-n', '--name', action='append', dest='names',
            help='name of the service to display (can be specified multiple times and wildchars are allowed)'
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

    def _create_services(self, config, config_filename):
        self.raw_config = config.dict()
        return super(Config, self)._create_services(config, config_filename, create_application=True)

    @staticmethod
    def match_service(names, name):
        if not names:
            return True

        for pattern in names:
            if len(pattern) != len(name):
                continue

            if all(starmap(fnmatchcase, zip(name, pattern))):
                return True

        return False

    @classmethod
    def compare(cls, config1, config2):
        r = {}

        for k, v in config2.items():
            if isinstance(v, dict):
                v = cls.compare(config1.get(k, {}), v)
                if v:
                    r[k] = v
            else:
                if k not in config1:
                    r[k] = v

        return r

    def run(self, names, not_modified, modified, application_service, services_service):
        names = [name.split('/') for name in (names or [])]

        if modified:

            def extract_infos(config, ancestors=()):
                infos = {}

                for k, v in config.items():
                    fullname = ancestors + (k,)

                    if self.match_service(names, fullname):
                        infos[k] = v

                    if isinstance(v, dict):
                        info = extract_infos(v, fullname)
                        if info:
                            infos[k] = info

                return infos

            config = extract_infos(self.raw_config)
        else:

            def extract_infos(config, ancestors=()):
                infos = {}

                for f, (entry, name, cls, plugin, children) in config:
                    if plugin is None:
                        continue

                    children = list(children)
                    children_names = set(child[1][1] for child in children)
                    fullname = ancestors + (name,)

                    if (plugin is not None) and self.match_service(names, fullname):
                        infos[name] = {
                            children_name: config
                            for children_name, config in plugin.plugin_config.items()
                            if children_name not in children_names
                        }

                    info = extract_infos(children, fullname)
                    if info:
                        config = {
                            children_name: config
                            for children_name, config in plugin.plugin_config.items()
                            if children_name not in children_names
                        }
                        infos[name] = dict(config, **info)

                return infos

            config = extract_infos(services_service.walk2('services'))
            if not_modified:
                config = self.compare(self.raw_config, config)

        if not config:
            print('<empty>')
            return 1

        print('Configuration')
        print('-------------')

        config_from_dict(config).display(
            4,
            filter_parameter=lambda param: (param == '___many___') or (not param.startswith('_'))
        )

        return 0
