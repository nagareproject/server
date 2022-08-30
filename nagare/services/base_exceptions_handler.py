# Encoding: utf-8

# --
# Copyright (c) 2008-2022 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from nagare import log
from nagare.services import plugin
from nagare.server import reference


def default_exception_handler(exception, exceptions_service, services_service, **context):
    exception = services_service(exceptions_service.handle_exception, exception, **context)

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
        services_service(
            super(ExceptionsService, self).__init__,
            name, dist,
            exception_handle=exception_handler,
            **config
        )

        self.exception_handler = reference.load_object(exception_handler)[0]
        self.services = services_service
        self.exception_handlers = []

    @staticmethod
    def log_exception(logger_name='nagare.services.exceptions', exc_info=True):
        log.get_logger(logger_name).error('Unhandled exception', exc_info=exc_info)

    def clear_exception_handlers(self):
        self.exception_handlers = []

    def add_exception_handler(self, exception_handler):
        if exception_handler not in self.exception_handlers:
            self.exception_handlers.append(exception_handler)

    def handle_exception(self, exception, services_service, **context):
        for exception_handler in self.exception_handlers:
            exception = services_service(exception_handler, exception, **context)

        return exception

    def handle_request(self, chain, **params):
        try:
            return chain.next(**params)
        except Exception as exception:
            return self.services(self.exception_handler, exception, **params)
