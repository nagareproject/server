from nagare.server import wsgi


def test_exception():
    class WSGIApp(wsgi.WSGIApp):
        def on_exception(self, request, response):
            response.body = 'KO'
            return response

        def handle_request(self, request, response):
            1 / 0

    body = WSGIApp()({'REQUEST_METHOD': 'GET'}, lambda status, header: None)
    assert body == ['KO']
