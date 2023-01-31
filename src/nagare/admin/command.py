# --
# Copyright (c) 2008-2023 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

"""The ``nagare-admin`` executable."""

import imp
import os

from nagare.admin import admin
from nagare.admin.admin import Banner, Commands  # noqa: F401
from nagare.config import InterpolationError
from nagare.packaging import Distribution
from nagare.server.services import NagareServices, Services


class AppCommands(Commands):
    DESC = 'applications management subcommands'


def get_roots(config, global_config):
    class Application(Services):
        def __init__(self):
            self.app_name = self.app_version = self.app_url = self.data = self.static = None
            self.package_path = self.module_path = None

            super(Application, self).__init__()

        def load_plugins(self, config, global_config):
            # Ignore all substituion errors
            class D(dict):
                def get(self, name):
                    return super(D, self).get(name, '')

            application = config['application']
            application_ori = application.dict()
            try:
                application.interpolate(D(global_config), ancestors_names=('application',))
            except InterpolationError:
                pass

            self.app_name = application.get('name')
            if self.app_name:
                application_ori['name'] = self.app_name

                self.app_url = '/' + application.get('url', '').strip('/')
                self.data = application.get('data')
                self.static = application.get('static')

                entries = dict(super(Application, self).iter_entry_points('application', 'nagare.applications', config))
                entry = entries.get(self.app_name)
                if entry is not None:
                    self.app_version = entry.dist.version

                    package_module = entry.module_name.rsplit('.', 1)
                    if len(package_module) == 1:
                        module_name = package_module[0]
                        paths = None
                    else:
                        module_name = package_module[1]
                        paths = list(__import__(package_module[0], fromlist=['']).__path__)

                    module_file, module_path, _ = imp.find_module(module_name, paths)
                    if module_file:
                        module_file.close()

                    self.module_path = os.path.dirname(module_path)
                    self.package_path = os.path.join(
                        Distribution(entry.dist).editable_project_location or entry.dist.location, self.app_name
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

        return super(Command, cls)._create_services(config, config_filename, roots, global_config, create_application)
