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
from itertools import dropwhile

from nagare import commands

from nagare.server.services import Services


class Command(commands.Command):
    """The base class of all the commands"""
    WITH_CONFIG_FILENAME = True
    WITH_STARTED_SERVICES = False

    def start(self, services_service, publisher_service=None, **params):
        if self.WITH_STARTED_SERVICES and publisher_service:
            services_service(publisher_service.create_app)

        return services_service(self.run, **params)

    def set_arguments(self, parser):
        super(Command, self).set_arguments(parser)

        if self.WITH_CONFIG_FILENAME:
            parser.add_argument('config_filename', nargs='?', help='Configuration file')

    def parse(self, command_name, args):
        arguments = super(Command, self).parse(command_name, args)

        if self.WITH_CONFIG_FILENAME:
            config_filename = arguments['config_filename']
            if config_filename is None:
                config_filename = os.environ.get('NAGARE_CONF')

            if config_filename is None:
                raise ValueError("config filename missing")

            if not os.path.exists(config_filename):
                raise ValueError("config filename <%s> doesn't exist" % config_filename)

            arguments['config_filename'] = os.path.abspath(os.path.expanduser(config_filename))

        return arguments

# ---------------------------------------------------------------------------


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
            self.app_name = config['application']['name']
            return config

        def load_activated_plugins(self, entries, activations=None):
            entries = {entry.name: entry for entry in entries}
            entry = entries[self.app_name]

            import_path = entry.module_name.split('.')
            if len(import_path) > 1:
                module = __import__('.'.join(import_path[:-1]))
                self.module_path = os.path.dirname(module.__file__)

            self.package_path = os.path.join(entry.dist.location, self.app_name)

            return []

    application = Application(config_filename, '', 'nagare.applications')

    return application.app_name, (application.package_path, application.module_path)


def run(args=None):
    command, arguments = commands.ConsoleScript('nagare.commands')(args)
    if command is None:
        return 2

    config_filename = arguments.pop('config_filename', None)

    config = Services().read_config(
        {'activated_by_default': 'boolean(default=True)'},
        config_filename, 'services'
    )

    app_name, roots = get_roots(config_filename)

    root_path = find_path(roots, '')
    data_path = find_path(roots, 'data')
    static_path = find_path(roots, 'static')

    services = Services(
        config_filename, '',
        'nagare.services',
        config['activated_by_default'],
        app_name=app_name,
        root=root_path, root_path=root_path,
        data=data_path, data_path=data_path,
        static=static_path, static_path=static_path,
        here=os.path.dirname(config_filename) if config_filename else '',
        **os.environ
    )

    return services(command.start, **arguments)
