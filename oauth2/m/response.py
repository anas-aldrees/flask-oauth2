from cStringIO import StringIO


class Response(object):

    def __init__(self, body, headers, status_code):
        self.body = body
        self.headers = headers
        self.status_code = status_code
