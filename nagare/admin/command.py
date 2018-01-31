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

from nagare import commands

from nagare.server.services import Services


class Command(commands.Command):
    """The base class of all the commands"""
    WITH_CONFIG_FILENAME = True
    WITH_STARTED_SERVICES = False

    def start(self, application_service, services_service, **params):
        if self.WITH_STARTED_SERVICES:
            app = application_service.create()

            for service in services_service.start_handlers.values():
                service.handle_start(app)

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


def run():
    command, arguments = commands.ConsoleScript('nagare.commands')()
    if command is None:
        return 2

    config_filename = arguments.pop('config_filename', None)

    config = Services().read_config(
        {'activated_by_default': 'boolean(default=True)'},
        config_filename, 'services'
    )

    services = Services(config_filename, '', 'nagare.services', config['activated_by_default'])

    return services(command.start, **arguments)
