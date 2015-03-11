from lib import util as utils
from lib.http import create_json_exception_response
from config.config import TOKEN_LENGTH, TOKEN_EXPIRES_IN, TOKEN_TYPE_BEARER, \
    AUTH_CODE_EXPIRES_IN

def generate_authorization_code():
    """Generate a random authorization code.

    :rtype: str
    """
    return utils.random_ascii_string(TOKEN_LENGTH)


def generate_access_token():
    """Generate a random access token.

    :rtype: str
    """
    return utils.random_ascii_string(TOKEN_LENGTH)


def generate_refresh_token():
    """Generate a random refresh token.

    :rtype: str
    """
    return utils.random_ascii_string(TOKEN_LENGTH)


def get_authorization_code(user_id,
                           response_type,
                           client_id,
                           redirect_uri,
                           scopes):
    """Generate authorization code HTTP response.

    :param response_type: Desired response type. Must be exactly "code".
    :type response_type: str
    :param client_id: Client ID.
    :type client_id: str
    :param redirect_uri: Client redirect URI.
    :type redirect_uri: str
    :rtype: {code: , response_type: , client_id: , redirect_uri: }
    """

    if response_type is None or client_id is None or redirect_uri is None:
        # TODO if redirect uri exists, redirect this error to it
        raise exceptions.InvalidRequest()
    # Ensure proper response_type
    if response_type != 'code':
        raise exceptions.UnsupportedResponseType()

    # Check redirect URI
    is_valid_redirect_uri = validate_redirect_uri(client_id,
                                                  redirect_uri)
    if not is_valid_redirect_uri:
        raise exceptions.InvalidRequest()

    # Check conditions
    is_valid_client_id = validate_client_id(client_id)
    is_valid_access = True
    is_valid_scope = validate_scope(client_id, scopes)

    # Return proper error responses on invalid conditions
    if not is_valid_client_id:
        raise exceptions.UnauthorizedClient()

    if not is_valid_access:
        raise exceptions.AccessDenied()

    if not is_valid_scope:
        raise exceptions.InvalidScope()

    # Generate authorization code
    code = generate_authorization_code()

    # Save information to be used to validate later requests
    persist_authorization_code(user_id=user_id,
                               client_id=client_id,
                               code=code,
                               scopes=scopes)

    return code


def get_new_access_token(
    grant_type,
    client_id,
    client_secret,
    refresh_token
):
    """Generate access token HTTP response from a refresh token.

    :param grant_type: Desired grant type. Must be "refresh_token".
    :type grant_type: str
    :param client_id: Client ID.
    :type client_id: str
    :param client_secret: Client secret.
    :type client_secret: str
    :param refresh_token: Refresh token.
    :type refresh_token: str
    :rtype: {access_token:, token_type:, expires_in}
    """

    # Ensure proper grant_type
    if grant_type == None and client_id == None and client_secret == None:
        raise exceptions.InvalidRequest()

    if grant_type != 'refresh_token':
        raise exceptions.InvalidGrant()

    # Check conditions
    # TODO why validating client, then validating client and secret??
    is_valid_client_id = validate_client_id(client_id)
    is_valid_client_secret = validate_client_secret(client_id,
                                                    client_secret)

    data = from_refresh_token(client_id, refresh_token)
    is_valid_refresh_token = data is not None

    # Return proper error responses on invalid conditions
    if not (is_valid_client_id and is_valid_client_secret):
        raise exceptions.InvalidClient()

    if not is_valid_refresh_token:
        raise exceptions.InvalidGrant()

    # Generate access tokens once all conditions have been met
    access_token = generate_access_token()

    # update access_token
    update_access_token(refresh_token, access_token)

    return {
        'access_token': access_token,
        'token_type': TOKEN_TYPE_BEARER,
        'expires_in': TOKEN_EXPIRES_IN
    }


def get_new_access_and_refresh_tokens(
    grant_type,
    client_id,
    client_secret,
    redirect_uri,
    code
):
    # Ensure proper grant_type
    if not (grant_type and client_id and
            client_secret and redirect_uri and code):
        raise exceptions.InvalidRequest()
    if grant_type != 'authorization_code':
        raise exceptions.UnsupportedGrantType()

    # Check conditions
    is_valid_client_id = validate_client_id(client_id)

    is_valid_client_secret = validate_client_secret(client_id,
                                                    client_secret)

    if not (is_valid_client_id and is_valid_client_secret):
        raise exceptions.InvalidClient

    is_valid_redirect_uri = validate_redirect_uri(client_id,
                                                  redirect_uri)

    scopes = get_authorization_code_scopes(code)
    user_id = from_authorization_code(client_id, code)

    is_valid_grant = user_id and scopes
    print 'grant is valid'
    # Return proper error responses on invalid conditions

    if not is_valid_grant or not is_valid_redirect_uri:
        raise exceptions.InvalidGrant()

    # Discard original authorization code
    discard_authorization_code(client_id, code)

    # Generate access tokens once all conditions have been met
    access_token = generate_access_token()
    token_type = TOKEN_TYPE_BEARER
    expires_in = TOKEN_EXPIRES_IN
    refresh_token = generate_refresh_token()

    # Save information to be used to validate later requests
    persist_token_information(client_id=client_id,
                              scopes=scopes,
                              access_token=access_token,
                              token_type=token_type,
                              expires_in=expires_in,
                              refresh_token=refresh_token,
                              user_id=user_id)

    return {
        'access_token': access_token,
        'token_type': token_type,
        'expires_in': expires_in,
        'refresh_token': refresh_token
    }


def validate_client_id(client_id):
    """Check that the client_id represents a valid application.

    :param client_id: Client id.
    :type client_id: str
    """
    client = db.session.query(Client).filter_by(id=client_id).first()
    return client is not None


def validate_client_secret(client_id, client_secret):
    """Check that the client secret matches the application secret.

    :param client_id: Client Id.
    :type client_id: str
    :param client_secret: Client secret.
    :type client_secret: str
    """
    client = db.session.query(Client).filter_by(
        id=client_id, secret=client_secret).first()
    return client is not None


def validate_redirect_uri(client_id, redirect_uri):
    """Validate that the redirect_uri requested is available for the app.

    :param redirect_uri: Redirect URI.
    :type redirect_uri: str
    """
    client = db.session.query(Client).filter_by(id=client_id).first()
    for uri in client.redirect_uris:
        if redirect_uri == uri.redirect_uri:
            return True
    return False


def validate_scope(client_id, scopes):
    """Validate that the scope requested is available for the app.

    :param client_id: Client id.
    :type client_id: str
    :param scope: Requested scope.
    :type scope: str
    """
    client = db.session.query(Client).filter_by(id=client_id).first()
    client_scopes = []
    for s in client.scopes:
        client_scopes.append(s.scope)
    return set(scopes).issubset(client_scopes)


def persist_authorization_code(user_id, client_id, code, scopes):
    """Store important session information (user_id) along with the
    authorization code to later allow an access token to be created.

    :param client_id: Client Id.
    :type client_id: str
    :param code: Authorization code.
    :type code: str
    :param scope: Scope.
    :type scope: str
    """
    scopes_objects = []
    for i in scopes:
        scopes_objects.append(
            db.session.query(Scope).filter_by(scope=i).first())

    code = AuthorizationCode(client_id=client_id,
                             user_id=user_id,
                             code=code,
                             scopes=scopes_objects)
    db.session.add(code)
    db.session.commit()


def persist_token_information(client_id, scopes, access_token,
                              token_type, expires_in, refresh_token,
                              user_id):
    """Save OAuth access and refresh token information.

    :param client_id: Client Id.
    :type client_id: str
    :param scope: Scope.
    :type scope: str
    :param access_token: Access token.
    :type access_token: str
    :param token_type: Token type (currently only Bearer)
    :type token_type: str
    :param expires_in: Access token expiration seconds.
    :type expires_in: int
    :param refresh_token: Refresh token.
    :type refresh_token: str
    :param data: Data from authorization code grant.
    :type data: mixed
    """
    token = Token(client_id=client_id,
                  user_id=user_id,
                  access_token=access_token,
                  token_type=token_type,
                  expires_in=expires_in,
                  refresh_token=refresh_token,
                  scopes=scopes)
    db.session.add(token)
    db.session.commit()


def update_access_token(refresh_token, access_token):
    db.session.query(Token).filter_by(refresh_token=refresh_token)\
        .update({Token.access_token: access_token})
    db.session.commit()


def from_authorization_code(client_id, code):
    """Get session data from authorization code.

    :param client_id: Client ID.
    :type client_id: str
    :param code: Authorization code.
    :type code: str
    :param scope: Scope to validate.
    :type scope: str
    :rtype: dict if valid else None
    """
    auth_code = db.session.query(AuthorizationCode).\
        filter_by(client_id=client_id, code=code).first()
    if auth_code:
        elapsed_time = utils.get_elapsed_time(str(auth_code.date_time))
        if elapsed_time != -1 or elapsed_time < AUTH_CODE_EXPIRES_IN:
            return auth_code.user_id
        else:
            return None
    else:
        return None


def from_refresh_token(client_id, refresh_token):
    """Get session data from refresh token.

    :param client_id: Client Id.
    :type client_id: str
    :param refresh_token: Refresh token.
    :type refresh_token: str
    :param scope: Scope to validate.
    :type scope: str
    :rtype: dict if valid else None
    """
    data = db.session.query(Token).\
        filter_by(client_id=client_id, refresh_token=refresh_token)\
        .first()
    return data if data else None


def get_authorization_code_scopes(code):
    auth_code = db.session.query(AuthorizationCode)\
        .filter_by(code=code).first()
    return auth_code.scopes if auth_code else None


def discard_authorization_code(client_id, code):
    """Delete authorization code from the store and returns its scopes.

    :param client_id: Client Id.
    :type client_id: str
    :param code: Authorization code.
    :type code: str
    """
    db.session.query(AuthorizationCode)\
        .filter_by(client_id=client_id, code=code).delete()
    db.session.commit()


def discard_refresh_token(client_id, refresh_token):
    """Delete refresh token from the store.

    :param client_id: Client Id.
    :type client_id: str
    :param refresh_token: Refresh token.
    :type refresh_token: str
    """
    db.session.query(Token)\
        .filter_by(client_id=client_id, refresh_token=refresh_token)\
        .delete()
    db.session.commit()


def discard_client_user_tokens(client_id, user_id):
    """Delete access and refresh tokens from the store.

    :param client_id: Client Id.
    :type client_id: str
    :param user_id: User Id.
    :type user_id: str

    """
    pass


def validate_access(request, scope):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            data = validate_access_token(request, scope)
            if data is not None:
                return function(data, *args, **kwargs)
            else:
                exception = exceptions.AccessDenied()
                return create_json_exception_response(
                    message=exception.message,
                    code=exception.code,
                    status_code=401
                )
        return wrapper
    return decorator


def validate_access_token(request, scope):
    """
    This will return resourse owner info (id) from access token if the access
    token is valid else return un authorized error
    """
    access_token = __get_access_token_from_request(request)
    return get_session_data_from_access_token(access_token, scope)


def __get_access_token_from_request(_request):
    """
    Retreve access token from request header
    """
    # return _request.headers.get('Authorization')
    return _request.args.get('access_token')


def get_session_data_from_access_token(access_token, scope):
    data = db.session.query(Token).join(Token.scopes).filter(
        Token.access_token == access_token, Scope.scope == scope).first()
    if data:
        elapsed_time = utils.get_elapsed_time(str(data.date_time))
        if elapsed_time < TOKEN_EXPIRES_IN:
            return data.user_id
    else:
        return None


def create_scope(scope, description):
    '''
    creates a new oauth2 scope and returns the generated scope id.
    '''
    id = utils.generate_uuid4()
    db.session.execute("""
        INSERT INTO oauth2_scopes (id, scope, description)
        VALUES ('%s', '%s', '%s');""" % (id, scope, description)
                       )
    return id


def create_client(id, name, secret, description, redirect_uris, scopes_ids):
    '''
    creates a new oauth2 client and returns the generated client id and secret.
    TODO: client id and secret must be generated automaticly...
    that means we should remove those params from this function
    '''
    # client
    db.session.execute("""
        INSERT INTO oauth2_clients (id ,name ,description ,secret)
        VALUES ('%s', '%s', '%s', '%s');""" % (id, name, description, secret))

    # client redirect_uris
    for redirect_uri in redirect_uris:
        db.session.execute("""
            INSERT INTO oauth2_clients_redirect_uris (client_id, redirect_uri)
            VALUES ('%s', '%s');""" % (id, redirect_uri))

    # client scopes
    for scope_id in scopes_ids:
        db.session.execute("""
            INSERT INTO oauth2_client_scopes (client_id, scope_id)
            VALUES ('%s', '%s');""" % (id, scope_id))
    return{'client_id': id, 'secret': secret}


def get_client_by_client_id(id):
    client = db.session.query(Client).filter_by(id=id).first()
    if client:
        return client
    else:
        raise exceptions.InvalidClient()
