# Encoding: utf-8

# --
# (C)opyright Net-ng 2008-2017
#
# This is a Net-ng proprietary source code.
# Any reproduction modification or use without prior written
# approval from Net-ng is strictly forbidden.
# --

"""Base class for an application managing gevent servers"""

from gevent import monkey, event
monkey.patch_all()  # Monkey patch the Python standard library

from . import app_base  # noqa: E402


class Servers(list):
    """Pool of servers"""

    def __init__(self, servers):
        """Initialization

        In:
          - ``servers`` -- list of gevent servers
        """
        super(Servers, self).__init__(servers)
        self.stop_event = event.Event()

    def stop(self):
        """Stop all the servers"""
        self.stop_event.set()  # Send the stop signal

    def start(self):
        """Start all the servers"""

        # 1. Start the servers
        for server in self:
            if not server.started:
                server.start()

        # 2. Wait for the signal to stop
        self.stop_event.wait()

        # 3. Stop the servers
        for server in self:
            if server.started:
                server.stop()


class App(app_base.App):

    def __init__(self, config_file, error, initial_conf=None):
        """Initialize the application from a configuration file

        In:
          - ``config_file`` -- the path to the configuration file
          - ``error`` -- the function to call in case of configuration errors
          - ``initial_conf`` -- other configuration parameters not read from
            the configuration file
        """
        self.servers = None
        super(App, self).__init__(config_file, error, initial_conf)

    def init(self, config_file, error, conf):
        """Initialize the application from a ``ConfigObj`` configuration object

        In:
          - ``config_file`` -- the path to the configuration file
          - ``error`` -- the function to call in case of configuration errors
          - ``conf`` -- ``ConfigObj`` configuration object
        """
        super(App, self).init(config_file, error, conf)
        self.servers = Servers(self.create_servers(conf))

    def create_servers(self, conf):
        """Create and configure the servers

        In:
          - ``conf`` -- ``ConfigObj`` configuration object

        Return:
          - the servers
        """
        return []

    def start(self):
        """Start the application"""
        self.servers.start()

    def stop(self):
        """Stop the application"""
        self.servers.stop()
