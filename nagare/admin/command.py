# --
# Copyright (c) 2008-2018 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

"""The ``nagare-admin`` executable
"""

import os
import sys
from itertools import dropwhile

from nagare import commands
from nagare.commands import ArgumentError
from nagare.server.services import Services

BANNER = '''\
   _   _
  | \ | | __ _  __ _  __ _ _ __ ___
  |  \| |/ _` |/ _` |/ _` | '__/ _ \
  | |\  | (_| | (_| | (_| | | |  __/
  |_| \_|\__,_|\__, |\__,_|_|  \___|
               |___/

                http://www.nagare.org\
'''


def find_path(choices, name):
    choices = filter(None, choices + (os.getcwd(),))
    if name:
        choices = [os.path.join(dir, name) for dir in choices]

    return next(dropwhile(lambda dir: not os.path.isdir(dir), choices), '')


def get_roots(config_filename):

    class Application(Services):
        def __init__(self, *args, **kw):
            self.app_name = self.package_path = self.module_path = None
            super(Application, self).__init__(*args, **kw)

        def read_config(self, spec, config, config_section, **initial_config):
            config = super(Application, self).read_config(spec, config, config_section, False, **initial_config)
            self.app_name = config.get('application', {'name': None}).get('name')

            return config

        def load_activated_plugins(self, activations=None):
            if self.app_name:
                entries = {entry.name: entry for entry in self.iter_entry_points()}
                entry = entries[self.app_name]

                import_path = entry.module_name.split('.')
                if len(import_path) > 1:
                    module = __import__('.'.join(import_path[:-1]))
                    self.module_path = os.path.dirname(module.__file__)

                self.package_path = os.path.join(entry.dist.location, self.app_name)

            return []

    application = Application(config_filename, '', 'nagare.applications')

    return application.app_name, (application.package_path, application.module_path)

# ---------------------------------------------------------------------------


class ArgumentParser(commands.ArgumentParser):
    def format_help(self):
        return BANNER + '\n\n\n' + super(ArgumentParser, self).format_help()


class Command(commands.Command):
    """The base class of all the commands"""
    WITH_CONFIG_FILENAME = True
    WITH_STARTED_SERVICES = False

    @staticmethod
    def _create_service(config_filename, activated_by_default):
        app_name, roots = get_roots(config_filename)

        root_path = find_path(roots, '')
        data_path = find_path(roots, 'data')
        static_path = find_path(roots, 'static')

        return Services(
            config_filename, '', 'nagare.services', activated_by_default,
            app_name=app_name,
            root=root_path, root_path=root_path,
            data=data_path, data_path=data_path,
            static=static_path, static_path=static_path,
            here=os.path.dirname(config_filename) if config_filename else '',
            config_filename=config_filename or '',
            **os.environ
        )

    def _run(self, config_filename=None, **args):
        config = Services().read_config(
            {'activated_by_default': 'boolean(default=True)'},
            config_filename, 'services'
        )

        services = self._create_service(config_filename, config['activated_by_default'])

        publisher = services.get('publisher')
        if self.WITH_STARTED_SERVICES and publisher:
            services(publisher.create_app)

        return services(self.run, **args)

    def _create_parser(self, name):
        return ArgumentParser(name, description=self.DESC)

    def set_arguments(self, parser):
        super(Command, self).set_arguments(parser)

        if self.WITH_CONFIG_FILENAME:
            parser.add_argument('config_filename', nargs='?', help='Configuration file')

    def parse(self, command_name, args):
        parser, arguments = super(Command, self).parse(command_name, args)

        if self.WITH_CONFIG_FILENAME:
            try:
                config_filename = arguments['config_filename']
                if config_filename is None:
                    config_filename = os.environ.get('NAGARE_CONF')

                if config_filename is None:
                    raise ArgumentError(message="config filename missing")

                if not os.path.exists(config_filename):
                    raise ArgumentError(message="config filename <%s> doesn't exist" % config_filename)

                arguments['config_filename'] = os.path.abspath(os.path.expanduser(config_filename))
            except ArgumentError:
                parser.print_usage(sys.stderr)
                raise

        return parser, arguments


class Commands(commands.Commands):
    def usage(self, names, args):
        print BANNER
        print
        print

        return super(Commands, self).usage(names, args)

# ---------------------------------------------------------------------------


def run():
    return Commands(entry_points='nagare.commands').execute()
