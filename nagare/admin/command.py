# --
# Copyright (c) 2008-2021 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

"""The ``nagare-admin`` executable
"""

import os
import imp

from nagare.admin import admin
from nagare.admin.admin import Banner  # noqa: F401
from nagare.admin.admin import Commands
from nagare.server.services import Services


class AppCommands(Commands):
    DESC = 'applications management subcommands'


def get_roots(config_filename):

    class Application(Services):
        def __init__(self, *args, **kw):
            self.app_name = self.app_url = self.data = self.static = self.package_path = self.module_path = None
            super(Application, self).__init__(*args, **kw)

        def read_config(self, spec, config, config_section, **initial_config):
            config = super(Application, self).read_config(spec, config, config_section, False, **initial_config)
            application = super(Application, self).read_config(
                spec,
                config.get('application', {}),
                config_section,
                **dict(
                    {k: v.replace('$', '$$') for k, v in os.environ.items()},
                    **initial_config
                )
            )

            self.app_name = application.get('name', '')
            app_url = application.get('url', '').strip('/')
            self.app_url = app_url and ('/' + app_url)
            self.data = application.get('data')
            self.static = application.get('static')

            return config

        def load_activated_plugins(self, activations=None):
            entries = {entry.name: entry for entry in self.iter_entry_points()}
            entry = entries.get(self.app_name)

            if entry is not None:
                package_module = entry.module_name.rsplit('.', 1)
                if len(package_module) == 1:
                    module_name = package_module[0]
                    paths = None
                else:
                    module_name = package_module[1]
                    paths = list(__import__(package_module[0], fromlist=['']).__path__)

                module_path = imp.find_module(module_name, paths)[1]
                self.module_path = os.path.dirname(module_path)

                self.package_path = os.path.join(entry.dist.location, self.app_name)

            return []

    application = Application(config_filename, '', 'nagare.applications')

    return application.app_name, application.app_url, application.data, application.static, (
        application.package_path,
        application.module_path
    )


class Command(admin.Command):
    """The base class of all the commands"""

    SERVICES_FACTORY = Services

    @classmethod
    def _create_services(cls, config, config_filename, **vars):
        app_name, app_url, data, static, roots = get_roots(config_filename)

        data_path = data or admin.find_path(roots, 'data')
        static_path = static or admin.find_path(roots, 'static')

        env_vars = dict({
            'app_name': app_name,
            'app_url': app_url,
            'data': data_path,
            'static': static_path,
            '_static_path': static_path
        }, **vars)

        return super(Command, cls)._create_services(config, config_filename, roots, **env_vars)
