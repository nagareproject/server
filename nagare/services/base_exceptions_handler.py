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


def default_exception_handler(exception, exceptions_service, **context):
    exceptions_service.log_exception()

    if getattr(exception, 'commit_transaction', False):
        return exception
    else:
        raise exception


class ExceptionsService(plugin.Plugin):
    LOAD_PRIORITY = 25
    CONFIG_SPEC = dict(
        plugin.Plugin.CONFIG_SPEC,
        exception_handler='string(default="nagare.services.base_exceptions_handler:default_exception_handler")'
    )

    def __init__(self, name, dist, exception_handler, services_service, **config):
        services_service(super(ExceptionsService, self).__init__, name, dist, **config)

        exception_handler = reference.load_object(exception_handler)[0]
        self.exception_handler = lambda exception, params: services_service(exception_handler, exception, **params)
        self.services = services_service

    @staticmethod
    def log_exception(logger_name='nagare.services.exceptions', exc_info=True):
        log.get_logger(logger_name).error('Unhandled exception', exc_info=exc_info)

    def handle_exception(self, exception, params):
        return self.services(self.exception_handler, exception, params)

    def handle_request(self, chain, **params):
        try:
            return chain.next(**params)
        except Exception as exception:
            return self.handle_exception(exception, params)
