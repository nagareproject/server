# --
# Copyright (c) 2008-2020 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

"""Scoped objects

Currently:

  - objects scoped to a worker, a handler of one or several requests
  - objects scoped to a request (i.e a scoped cleared on each new request)
"""

import threading

from nagare.services import plugin


class Thread(threading.local):
    """Objects with attributes scoped to the current thread
    """
    def clear(self):
        self.__dict__.clear()

    @staticmethod
    def create_lock():
        return threading.Lock()


class DummyLock(object):
    acquire = release = __enter__ = __exit__ = lambda *args: True


class Process(object):
    """Objects with attributes scoped to the process
    """
    def clear(self):
        self.__dict__.clear()

    @staticmethod
    def create_lock():
        return DummyLock()

# ----------------------------------------------------------------------------


class Local(plugin.Plugin):
    LOAD_PRIORITY = 40

    def __init__(self, name, dist, publisher_service=None):
        global worker, request

        super(Local, self).__init__(name, dist)

        if publisher_service:
            publisher = publisher_service.service

            if publisher is not None:
                worker = Thread() if publisher.has_multi_threads else Process()
                request = Thread() if publisher.has_multi_threads else Process()

    @property
    def worker(self):
        global worker
        return worker

    @property
    def request(self):
        global request
        return request

    @staticmethod
    def handle_request(chain, **kw):
        global request

        request.clear()

        return chain.next(**kw)

# ----------------------------------------------------------------------------


worker = None
request = None
