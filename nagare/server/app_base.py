# Encoding: utf-8

# --
# (C)opyright Net-ng 2008-2017
#
# This is a Net-ng proprietary source code.
# Any reproduction modification or use without prior written
# approval from Net-ng is strictly forbidden.
# --

"""Base class for an application

Features:

  - global configuration file
  - logging subsystem configuration
  - services injection
"""

import logging.config

import configobj
from nagare.services import services, config


class App(object):
    CONFIG_SPEC = {
        'logging': {
            'level': 'string(default="NOTSET")',
            'formatters': {'keys': 'string(default="")'},
            'handlers': {'keys': 'string(default="")'},
            'loggers': {'keys': 'string(default="root")'},
            'logger_root': {
                'level': 'string(default="NOTSET")',
                'handlers': 'string(default="")'
            }
        }
    }

    def __init__(self, config_file, error, initial_conf=None):
        """Initialize the application from a configuration file

        In:
          - ``config_file`` -- the path to the configuration file
          - ``error`` -- the function to call in case of configuration errors
          - ``initial_conf`` -- other configuration parameters not read from
            the configuration file
        """
        self.services = None

        # Read the application configuration file and validate it
        conf = configobj.ConfigObj(
            config_file,
            configspec=configobj.ConfigObj(self.CONFIG_SPEC),
            list_values=False, interpolation='Template'
        )
        conf.merge(initial_conf or {})
        config.validate(config_file, conf, error)

        logging.addLevelName(10000, 'NONE')

        self.init(config_file, error, conf)

    def init(self, config_file, error, conf):
        """Initialize the application from a ``ConfigObj`` configuration object

        In:
          - ``config_file`` -- the path to the configuration file
          - ``error`` -- the function to call in case of configuration errors
          - ``conf`` -- ``ConfigObj`` configuration object
        """
        default_level = getattr(logging, conf['logging'].pop('level'))
        logging.basicConfig(level=default_level)

        # Configure the logging subsystem
        '''
        log_conf = ''
        for' k, v in conf['logging'].items():
            log_conf += '\n[%s]\n' % k
            log_conf += '\n'.join(map('='.join, v.items()))

        logging.config.fileConfig(StringIO.StringIO(log_conf))
        '''

        # Configure the services
        self.services = self.create_services(config_file, error, conf)

    def create_services(self, config_file, error, conf, entry_points=None):
        """Load and configure the services

        In:
          - ``config_file`` -- the path to the configuration file
          - ``error`` -- the function to call in case of configuration errors
          - ``conf`` -- ``ConfigObj`` configuration object
          - ``entry_points`` -- section of the services entry points

        Return:
          - the services registry
        """
        return services.Services(config_file, error, conf, entry_points)

    def start_with_services(self):
        """Start the application with services injection"""
        self.services(self.start)

    def start(self):
        """Start the application"""
        pass

    def stop(self):
        """Stop the application"""
        pass
