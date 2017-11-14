# Encoding: utf-8

# --
# (C)opyright Net-ng 2008-2017
#
# This is a Net-ng proprietary source code.
# Any reproduction modification or use without prior written
# approval from Net-ng is strictly forbidden.
# --

"""Gevent REST API server"""

import os
import logging

from gevent import monkey, wsgi
from gevent import socket as gsocket

monkey.patch_all()  # Monkey patch the Python standard library

logger = logging.getLogger(__name__)


class GeventPublisher(wsgi.WSGIServer):
    """REST API server"""

    CONFIG_SPEC = {
        'socket': 'string(default=None)',  # Unix socket to listen on
        'mode': 'integer(default=384)',  # RW mode of the unix socket
        'host': 'string(default="127.0.0.1")',  # TCP host to listen on
        'port': 'integer(default=80)',  # TCP port to listen on
        'backlog': 'integer(default=256)'  # Max nb of waiting requests
    }

    def __init__(
            self,
            wsgi_app,
            host='127.0.0.1', port=80,
            socket=None, mode=0600,
            backlog=256,
            *args, **kw
    ):
        if socket:
            # Create a unix socket
            listener = gsocket.socket(gsocket.AF_UNIX, gsocket.SOCK_STREAM)
            if os.path.exists(socket):
                os.remove(socket)
            listener.bind(socket)
            listener.listen(backlog)
            os.chmod(socket, mode)
            backlog = None
        else:
            # Create a TCP socket
            listener = (host, port)

        logger = logging.getLogger(__name__ + '.access')
        logger.write = lambda msg: logger.info(msg.rstrip())

        super(GeventPublisher, self).__init__(listener, wsgi_app, log=logger, backlog=self.backlog, *args, **kw)

    def serve(self):
        """Start the server"""
        msg = ('Serving Rest API on %s' + (':%d' if isinstance(self.address, tuple) else '')) % self.address
        print msg
        logger.info(msg)

        self.serve_forever()
