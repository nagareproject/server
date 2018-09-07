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

from nagare.admin import admin
from nagare.admin.admin import Commands  # noqa: F401
from nagare.server.services import Services


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


class Command(admin.Command):
    """The base class of all the commands"""

    SERVICES_FACTORY = Services

    def _create_service(self, config_filename, activated_by_default, **vars):
        app_name, roots = get_roots(config_filename)

        data_path = admin.find_path(roots, 'data')
        static_path = admin.find_path(roots, 'static')

        return super(Command, self)._create_service(
            config_filename, activated_by_default, roots,
            app_name=app_name,
            data=data_path, data_path=data_path,
            static=static_path, static_path=static_path,
            **vars
        )
