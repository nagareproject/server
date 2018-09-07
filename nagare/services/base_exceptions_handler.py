# Encoding: utf-8

# --
# Copyright (c) 2008-2018 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

import sys

from nagare import log
from nagare.services import plugin
from nagare.server import reference


def default_handler(exception, exception_service, **context):
    exception_service.log_exception()
    raise


class Handler(plugin.Plugin):
    LOAD_PRIORITY = 60
    CONFIG_SPEC = {
        'simplified': 'boolean(default=True)',
        'propagation': 'boolean(default=False)',
        'handler': 'string(default="nagare.services.base_exceptions_handler:default_handler")',
    }

    def __init__(self, name, dist, simplified, propagation, handler, services_service):
        super(Handler, self).__init__(name, dist)

        self.simplified = simplified
        self.propagation = propagation
        handler = reference.load_object(handler)[0]
        self.handler = lambda exception, **params: handler(self, exception, **params)
        self.services = services_service

    def log_exception(self, logger_name='nagare.services.exceptions', exc_info=None):
        exc_type, exc_value, exc_traceback = exc_info or sys.exc_info()

        tb = last_chain_seen = exc_traceback
        while self.simplified and tb:
            func_name = tb.tb_frame.f_code.co_name
            tb = tb.tb_next
            if func_name == 'handle_request':
                last_chain_seen = tb

        if not last_chain_seen:
            last_chain_seen = exc_traceback

        logger = log.get_logger(logger_name)
        logger.error('Unhandled exception', exc_info=(exc_type, exc_value, last_chain_seen))

        del exc_info, exc_traceback, last_chain_seen, tb

    def handle_request(self, chain, **params):
        try:
            return chain.next(**params)
        except Exception as exception:
            if self.propagation:
                raise

            return self.services(self.handler, exception, **params)
