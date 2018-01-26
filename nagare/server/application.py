# Encoding: utf-8

# --
# Copyright (c) 2008-2018 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

import os
import sys

from nagare.services import plugin


class RequestHandlersChain(list):

    def next(self, *args, **params):
        return self.pop(0).handle_request(self, *args, **params)

# ---------------------------------------------------------------------------


class App(plugin.Plugin):
    CONFIG_SPEC = {'simplified_exceptions': 'boolean(default=True)'}

    def __init__(self, name, dist, simplified_exceptions, services_service):
        """Initialization
        """
        self.name = name
        self.version = dist and dist.version
        self.simplified_exceptions = simplified_exceptions
        self.request_handlers = services_service.request_handlers.values()

    def handle_request(self, chain, **kw):
        return None

    def __call__(self, **params):
        try:
            response = RequestHandlersChain(self.request_handlers).next(**params)
        except:
            this_file = os.path.basename(__file__)

            exc_type, exc_value, exc_traceback = sys.exc_info()

            tb = last_chain_seen = exc_traceback
            while self.simplified_exceptions and tb:
                filename = tb.tb_frame.f_code.co_filename
                tb = tb.tb_next
                if filename.endswith('/' + this_file):
                    last_chain_seen = tb.tb_next

            try:
                raise exc_type, exc_value, last_chain_seen
            finally:
                del exc_traceback, last_chain_seen, tb

        return response
