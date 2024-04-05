# --
# Copyright (c) 2008-2024 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from fnmatch import fnmatchcase
from itertools import starmap

from nagare.admin import command
from nagare.config import config_from_dict


class Spec(command.Command):
    DESC = 'display the services configuration help'

    def __init__(self, name, dist, **config):
        self.config = None
        super(Spec, self).__init__(name, dist, **config)

    def set_arguments(self, parser):
        parser.add_argument(
            '-n',
            '--name',
            action='append',
            dest='names',
            help='name of the service to display (can be specified multiple times and wildchars are allowed)',
        )

        super(Spec, self).set_arguments(parser)

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

    def _create_services(self, config, config_filename):
        self.config = config
        return super(Spec, self)._create_services(config, config_filename, create_application=True)

    def run(self, names, services_service, application_service=None):
        names = [name.split('/') for name in (names or [])]

        def extract_infos(spec, ancestors=()):
            infos = {}

            for f, args in spec:
                name, config_spec, children = f(*args)
                fullname = ancestors + (name,)

                if self.match_service(names, fullname):
                    infos[name] = config_spec

                info = extract_infos(children, fullname)
                if info:
                    infos[name] = dict(config_spec, **info)

            return infos

        services = services_service.walk1(
            'services', 'nagare.services', self.config or {}, {}, services_service.activated_by_default
        )
        spec = extract_infos(services)
        if not spec:
            print('<empty>')
            return 1

        spec = config_from_dict(spec)
        spec.display(
            4, filter_parameter=lambda param: (param in ('__many__', '___many___')) or (not param.startswith('_'))
        )

        return 0


class Spec2(Spec):
    WITH_CONFIG_FILENAME = False

    def _create_services(self, config, config_filename):
        self.config = config
        return self.SERVICES_FACTORY()
