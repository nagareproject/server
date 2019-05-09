# Encoding: utf-8

# --
# Copyright (c) 2008-2019 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from nagare import log
from nagare.services import plugin
from nagare.server import reference


def default_handler(exception, exceptions_service, **context):
    exceptions_service.log_exception()
    return 0


class Handler(plugin.Plugin):
    LOAD_PRIORITY = 60
    CONFIG_SPEC = dict(
        plugin.Plugin.CONFIG_SPEC,
        handler='string(default="nagare.services.base_exceptions_handler:default_handler")'
    )

    def __init__(self, name, dist, handler, services_service, **config):
        services_service(super(Handler, self).__init__, name, dist, **config)

        handler = reference.load_object(handler)[0]
        self.handler = lambda exception, services_service, **params: services_service(handler, exception, **params)
        self.services = services_service

    def log_exception(self, logger_name='nagare.services.exceptions', exc_info=True):
        log.get_logger(logger_name).error('Unhandled exception', exc_info=exc_info)

    def handle_request(self, chain, **params):
        try:
            return chain.next(**params)
        except Exception as exception:
            return self.services(self.handler, exception, **params)
