from oauthh.oauthh_exception import oauthhException
from config.errors import OAUTH2_INVALID_CLIENT_CODE, \
    OAUTH2_INVALID_GRANT_CODE, OAUTH2_UNSUPPORTED_GRANT_TYPE_CODE,\
    OAUTH2_INVALID_REQUEST_CODE, OAUTH2_INVALID_SCOPE_CODE, \
    OAUTH2_INVALID_CLIENT_MESSAGE, OAUTH2_INVALID_GRANT_MESSAGE, \
    OAUTH2_UNSUPPORTED_GRANT_TYPE_MESSAGE, OAUTH2_INVALID_REQUEST_MESSAGE,\
    OAUTH2_INVALID_SCOPE_MESSAGE, OAUTH2_UNSUPPORTED_RESPONSE_TYPE_CODE, \
    OAUTH2_UNSUPPORTED_RESPONSE_TYPE_MESSAGE, \
    OAUTH2_UNAUTHORIZED_CLIENT_MESSAGE, OAUTH2_ACCESS_DENIED_MESSAGE, \
    OAUTH2_UNAUTHORIZED_CLIENT_CODE, OAUTH2_ACCESS_DENIED_CODE


class OAuth2Exception(oauthhException):
    pass


class InvalidClient(OAuth2Exception):

    def __init__(self):
        self.code = OAUTH2_INVALID_CLIENT_CODE
        self.message = OAUTH2_INVALID_CLIENT_MESSAGE

    def __str__(self):
        return "Error, code=[%s] message=[%s]" % (self.code, self.node_code)


class InvalidScope(OAuth2Exception):

    def __init__(self):
        self.code = OAUTH2_INVALID_SCOPE_CODE
        self.message = OAUTH2_INVALID_SCOPE_MESSAGE

    def __str__(self):
        return "Error, code=[%s] message=[%s]" % (self.code, self.node_code)


class InvalidGrant(OAuth2Exception):

    def __init__(self):
        self.code = OAUTH2_INVALID_GRANT_CODE
        self.message = OAUTH2_INVALID_GRANT_MESSAGE

    def __str__(self):
        return "Error, code=[%s] message=[%s]" % (self.code, self.node_code)


class InvalidRequest(OAuth2Exception):

    def __init__(self):
        self.code = OAUTH2_INVALID_REQUEST_CODE
        self.message = OAUTH2_INVALID_REQUEST_MESSAGE

    def __str__(self):
        return "Error, code=[%s] message=[%s]" % (self.code, self.node_code)


class UnsupportedGrantType(OAuth2Exception):

    def __init__(self):
        self.code = OAUTH2_UNSUPPORTED_GRANT_TYPE_CODE
        self.message = OAUTH2_UNSUPPORTED_GRANT_TYPE_MESSAGE

    def __str__(self):
        return "Error, code=[%s] message=[%s]" % (self.code, self.node_code)


class UnsupportedResponseType(OAuth2Exception):

    def __init__(self):
        self.code = OAUTH2_UNSUPPORTED_RESPONSE_TYPE_CODE
        self.message = OAUTH2_UNSUPPORTED_RESPONSE_TYPE_MESSAGE

    def __str__(self):
        return "Error, code=[%s] message=[%s]" % (self.code, self.node_code)


class UnauthorizedClient(OAuth2Exception):

    def __init__(self):
        self.code = OAUTH2_UNAUTHORIZED_CLIENT_CODE
        self.message = OAUTH2_UNAUTHORIZED_CLIENT_MESSAGE

    def __str__(self):
        return "Error, code=[%s] message=[%s]" % (self.code, self.node_code)


class AccessDenied(OAuth2Exception):

    def __init__(self):
        self.code = OAUTH2_ACCESS_DENIED_CODE
        self.message = OAUTH2_ACCESS_DENIED_MESSAGE

    def __str__(self):
        return "Error, code=[%s] message=[%s]" % (self.code, self.node_code)
