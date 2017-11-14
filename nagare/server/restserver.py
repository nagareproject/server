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
import traceback

import webob
from webob import exc

from gevent import wsgi
from gevent import socket as gsocket

logger = logging.getLogger(__name__)


class WSGIApp(object):
    """WSGI application to handle a REST request"""

    def __init__(self, router_service, services_service):
        """Initialization

        In:
          - ``router_service`` -- the URL dispatcher service
          - ``services_service`` -- the services repository
        """
        self.router = router_service
        self.services = services_service

    def create_request(self, environ):
        """Parse the REST environment received

        In:
          - ``environ`` -- the WSGI environment

        Return:
          - a ``WebOb`` Request object
        """
        return webob.Request(environ, charset='utf-8')

    def create_response(self, request, body):
        """Return a response to the client

        In:
          - ``request`` -- the ``WebOb`` Request object
          - ``body`` -- the response body

        Return:
          - a ``WebOb`` Response object
        """
        return webob.Response(json_body=body)

    def create_dispatch_args(self, request):
        """Create the arguments that will be passed to the routing service

        In:
          - ``request`` -- the ``WebOb`` Request object

        Return:
          - the arguments
        """
        url = request.path_info.strip('/').split('/')

        # By default, the dispatch starts from this object,
        # using the HTTP method and the url
        return self, request.method, tuple(url), request

    def __call__(self, environ, start_response):
        """The WSGI entry point

        In:
          - ``environ`` -- the WSGI environment
          - ``start_response`` -- the WSGI response callback

        Return:
          - the content (an iterator) to sent back to the client
        """
        request = self.create_request(environ)

        args = self.create_dispatch_args(request)
        params = dict(request.GET)

        try:
            while isinstance(args, tuple):
                args = self.router(*args, **params) or ''
        except exc.HTTPException as response:
            pass
        except TypeError as e:
            traceback.print_exc()
            logger.error(unicode(e))
            response = exc.HTTPBadRequest('invalid parameters')
        except Exception as e:
            logger.critical('', exc_info=1)
            response = exc.HTTPInternalServerError()
        else:
            response = self.create_response(request, args)

        return response(environ, start_response)


class Server(wsgi.WSGIServer):
    """REST API server"""

    CONFIG_SPEC = {
        'socket': 'string(default=None)',  # Unix socket to listen on
        'mode': 'integer(default=384)',  # RW mode of the unix socket
        'host': 'string(default="127.0.0.1")',  # TCP host to listen on
        'port': 'integer(default=80)',  # TCP port to listen on
        'backlog': 'integer(default=256)'  # Max nb of waiting requests
    }

    WSGI_FACTORY = WSGIApp  # Default WSGI application to handle the request

    def __init__(
            self,
            services_service, socket=None,
            host='127.0.0.1', mode=0600, port=80,
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

        wsgi_app = services_service(self.WSGI_FACTORY, *args, **kw)

        super(Server, self).__init__(listener, wsgi_app, log=logger, backlog=backlog)

    def start(self):
        """Start the server"""
        msg = ('Serving Rest API on %s' + (':%d' if isinstance(self.address, tuple) else '')) % self.address
        print msg
        logger.info(msg)

        super(Server, self).start()
