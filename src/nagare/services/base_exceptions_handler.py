# --
# Copyright (c) 2014-2025 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from nagare import log
from nagare.server import reference
from nagare.services import plugin


def exception_handler(exception, exceptions_service, **context):
    exceptions_service.log_exception()
    return exception


class ExceptionsService(plugin.Plugin):
    LOAD_PRIORITY = 25
    CONFIG_SPEC = plugin.Plugin.CONFIG_SPEC | {
        'exception_handlers': 'string_list(default=list("nagare.services.base_exceptions_handler:exception_handler"))',
        'commit_exceptions': 'string_list(default=list())',
    }

    def __init__(self, name, dist, exception_handlers, commit_exceptions, services_service, **config):
        services_service(
            super().__init__,
            name,
            dist,
            exception_handlers=exception_handlers,
            commit_exceptions=commit_exceptions,
            **config,
        )

        self.exception_handlers = [reference.load_object(handler)[0] for handler in exception_handlers]
        self.commit_exceptions = tuple(reference.load_object(exception)[0] for exception in commit_exceptions)
        self.services = services_service

    @staticmethod
    def log_exception(logger_name='nagare.services.exceptions', exc_info=True):
        log.get_logger(logger_name).error('Unhandled exception', exc_info=exc_info)

    def must_commit(self, exception):
        return isinstance(exception, self.commit_exceptions)

    def clear_exception_handlers(self):
        self.exception_handlers = []

    def add_exception_handler(self, exception_handler):
        if exception_handler not in self.exception_handlers:
            self.exception_handlers.append(exception_handler)

    def handle_request(self, chain, **params):
        try:
            return chain.next(**params)
        except Exception as exception:
            for exception_handler in self.exception_handlers:
                exception = self.services(exception_handler, exception, **params)

            return exception
