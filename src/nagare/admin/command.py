# --
# Copyright (c) 2014-2025 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

"""The ``nagare-admin`` executable."""

import os
from importlib.util import find_spec

from nagare.admin import admin
from nagare.config import InterpolationError
from nagare.packaging import Distribution
from nagare.admin.admin import Banner, Commands  # noqa: F401
from nagare.server.services import Services, NagareServices


class AppCommands(Commands):
    DESC = 'applications management subcommands'


def get_roots(config, global_config):
    class Application(Services):
        def __init__(self):
            self.app_name = self.app_version = self.app_url = self.data = self.static = None
            self.package_path = self.module_path = None

            super().__init__()

        def load_plugins(self, config, global_config):
            application = config['application']
            application_ori = application.dict()
            try:
                application.interpolate(global_config, ancestors_names=('application',))
            except InterpolationError:
                # Ignore all substitution errors
                pass

            self.app_name = application.get('name')
            if self.app_name:
                application_ori['name'] = self.app_name

                self.app_url = '/' + application.get('url', '').strip('/')
                self.data = application.get('data')
                self.static = application.get('static')

                entries = {
                    name: (dist, entry)
                    for dist, name, entry in super().iter_entry_points('application', 'nagare.applications', config)
                }

                if self.app_name in entries:
                    dist, entry = entries[self.app_name]
                    self.app_version = dist.version

                    parent_module_name = entry.value.split(':', 1)[0].rsplit('.', 1)[0]
                    parent_module_spec = find_spec(parent_module_name)
                    if parent_module_spec is None:
                        raise ModuleNotFoundError("No module named '{}'".format(parent_module_name))

                    self.module_path = os.path.dirname(parent_module_spec.origin)
                    self.package_path = os.path.join(
                        Distribution(dist).editable_project_location or str(dist.locate_file('')), self.app_name
                    )

            application.from_dict(application_ori)

    application = Application()
    if config is not None:
        application.load_plugins(config, global_config)

    return (
        application.app_name,
        application.app_version,
        application.app_url,
        application.data,
        application.static,
        (application.package_path, application.module_path),
    )


class Command(admin.Command):
    """The base class of all the commands."""

    SERVICES_FACTORY = NagareServices

    @classmethod
    def _create_services(cls, config, config_filename, create_application=False):
        global_config = {k: v.replace('$', '$$') for k, v in os.environ.items()}
        if config_filename:
            global_config['here'] = os.path.dirname(config_filename)

        app_name, app_version, app_url, data, static, roots = get_roots(config, global_config)

        data_path = data or admin.find_path(roots, 'data')
        static_path = static or admin.find_path(roots, 'static')

        global_config.update(
            {
                'app_name': app_name,
                'app_version': app_version,
                'app_url': app_url,
                'data': data_path,
                'static': static_path,
                '_static_path': static_path,
            }
        )

        return super()._create_services(config, config_filename, roots, global_config, create_application)
