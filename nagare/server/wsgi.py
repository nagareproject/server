# Encoding: utf-8

# --
# (C)opyright Net-ng 2008-2017
#
# This is a Net-ng proprietary source code.
# Any reproduction modification or use without prior written
# approval from Net-ng is strictly forbidden.
# --

import sys

import webob
from webob import exc


class Request(webob.Request):
    def __init__(self, environ, *args, **kw):
        super(Request, self).__init__(environ, *args, **kw)

    @property
    def is_xhr(self):
        return super(Request, self).is_xhr or ('_a' in self.params)

    def create_redirect_response(self, location=None):
        r = webob.exc.HTTPTemporaryRedirect(location=location)
        if self.is_xhr:
            r.status = exc.HTTPServiceUnavailable.code

        return r


class Response(webob.Response):
    pass


class WSGIApp(object):
    """WSGI application to handle a REST request"""

    def __init__(self, services_service=None):
        """Initialization

        In:
          - ``services_service`` -- the services repository
        """
        self.project_name = None
        self.project_version = None
        self.last_exception = None

        self.services = services_service

    def set_project_name(self, name):
        self.project_name = name

    def set_project_version(self, version):
        self.project_version = version

    def start(self):
        pass

    def on_exception(self, request, response):
        raise

    def create_request(self, environ, *args, **kw):
        """Parse the REST environment received

        In:
          - ``environ`` -- the WSGI environment

        Return:
          - a ``WebOb`` Request object
        """
        return Request(environ, charset='utf-8', *args, **kw)

    def create_response(self, request, *args, **kw):
        """Return a response to the client

        In:
          - ``request`` -- the ``WebOb`` Request object

        Return:
          - a ``WebOb`` Response object
        """
        return Response(*args, **kw)

    def handle_request(self, request, response):
        response.content_type = 'text/plain'
        response.content = ''

        return response

    def __call__(self, environ, start_response):
        """The WSGI entry point

        In:
          - ``environ`` -- the WSGI environment
          - ``start_response`` -- the WSGI response callback

        Return:
          - the content (an iterator) to sent back to the client
        """
        request = self.create_request(environ)
        response = self.create_response(request)

        self.last_exception = None

        try:
            response = self.handle_request(request, response)
        except exc.HTTPException, response:
            pass
        except Exception:
            self.last_exception = (request, sys.exc_info())
            response = self.on_exception(request, response)

        return response(environ, start_response)
