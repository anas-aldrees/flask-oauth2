from flask import request, redirect, url_for, session, Blueprint
import oauthh.oauth2.c.c_oauth2 as c_oauth2
from config.config import OFFICIAL_oauthh_WEBSITE_CLIENT_ID
from config.config import OFFICIAL_oauthh_ANDROID_CLIENT_ID
from oauthh.oauthh_exception import oauthhException
from oauthh.oauth2.m.exceptions import InvalidRequest, UnsupportedGrantType
import lib.http as http
import traceback
import sys

api_v1_bp = Blueprint('oauth2', __name__, template_folder='templates')

@api_v1_bp.route('/auth', methods=['GET', 'POST'])
def authorization_code():
    try:
        this_url = request.url
        client_id = request.args.get('client_id')
        scopes = request.args.get('scope').split(' ')
        redirect_uri = request.args.get('redirect_uri')
        response_type = request.args.get('response_type')

        if 'user_id' not in session:
            return __redirect_to_authenticate(this_url)

        # if grant templete not viewed to the user
        if request.args.get('sent') != 'true':

            # no need to grant user if the client was official website
            if client_id == OFFICIAL_oauthh_WEBSITE_CLIENT_ID \
                    or client_id == OFFICIAL_oauthh_ANDROID_CLIENT_ID:
                code = c_oauth2.get_authorization_code(
                    user_id=session['user_id'],
                    client_id=client_id,
                    scopes=scopes,
                    redirect_uri=redirect_uri,
                    response_type=response_type
                )
                return __create_authorization_code_response(
                    code=code,
                    redirect_uri=redirect_uri
                )

            else:
                client = c_oauth2.get_client_by_client_id(id=client_id)
                return __render_grant_template()
        elif request.args.get('sent') == 'true':
            if request.args.get('allow') == 'allow':
                code = c_oauth2.get_authorization_code(
                    user_id=session['user_id'],
                    client_id=client_id,
                    scopes=scopes,
                    redirect_uri=redirect_uri,
                    response_type=response_type
                )
                return __create_authorization_code_response(
                    code=code,
                    redirect_uri=redirect_uri
                )
            else:
                return 'not allowed'
    except oauthhException as se:
        if redirect_uri is not None and \
            not isinstance(se, InvalidRequest) and \
                redirect_uri != 'title':
            return __create_redirect_exception_response(
                redirect_uri=redirect_uri,
                error_code=se.code,
                error_message=se.message
            )
        else:
            # can't redirect the error to the client, so, no redirect
            return http.create_json_exception_response(
                code=se.code,
                message=se.message,
                status_code=400
            )
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        if redirect_uri is not None:
            return __create_redirect_exception_response(
                redirect_uri=redirect_uri,
                error_code='N/A',
                error_message='server_error'
            )
        else:
            # can't redirect the error to the client, so, no redirect
            return http.create_json_exception_response(
                code='N/A',
                message='N/A',
                status_code=400
            )


@api_v1_bp.route('/token', methods=['POST'])
def token():
    try:
        # TODO form params must not included more than once
        grant_type = request.form.get('grant_type')
        client_id = request.form.get('client_id')
        client_secret = request.form.get('client_secret')
        refresh_token = request.form.get('refresh_token')
        code = request.form.get('code')
        redirect_uri = request.form.get('redirect_uri')

        if grant_type == 'authorization_code':
            data = c_oauth2.get_new_access_and_refresh_tokens(
                grant_type=grant_type,
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                code=code
            )
            print data
            return __create_tokens_response(data=data)
        elif grant_type == 'refresh_token':
            data = c_oauth2.get_new_access_token(
                grant_type=grant_type,
                client_id=client_id,
                client_secret=client_secret,
                refresh_token=refresh_token
            )
            print data
            return __create_tokens_response(data=data)
        else:
            raise UnsupportedGrantType()

    except oauthhException as se:
        # TODO redirect or not??
        return http.create_json_exception_response(
            code=se.code,
            message=se.message,
            status_code=400
        )
    except Exception:
        traceback.print_exc(file=sys.stdout)
        return http.create_json_exception_response()


def __create_authorization_code_response(code, redirect_uri):
    if redirect_uri == 'title':
        return http.create_response(
            body='<title>%s</title>' % code,
            headers={
                'Content-Type': 'text/html',
            },
            status_code=200
        )
    else:
        response = http.create_response(
            headers={
                'Cache-Control': 'no-store',
                'Pragma': 'no-cache',
                'Location': http.build_url(
                    redirect_uri, {'code': code}
                )
            },
            status_code=302
        )
        return response


def __create_tokens_response(data):
    return http.create_json_response(
        data=data,
        headers={
            'Cache-Control': 'no-store',
            'Pragma': 'no-cache',
        },
        status_code=200
    )


def __create_redirect_exception_response(
    redirect_uri,
    error_code='N/A',
    error_message='N/A'
):
    return http.create_response(
        headers={
            'Cache-Control': 'no-store',
            'Pragma': 'no-cache',
            'Location': http.build_url(
                redirect_uri, {
                    'error_code': error_code,
                    'error_message': error_message
                }
            )
        },
        status_code=302
    )


def __redirect_to_authenticate(continue_url):
    return http.create_response(
        headers={
            'Cache-Control': 'no-store',
            'Pragma': 'no-cache',
            'Location': http.build_url(
                url_for('authenticate'), {
                    'continue_url': continue_url
                }
            )
        },
        status_code=302
    )


def __render_grant_template():
    return 'grant not implemented yet!!'
