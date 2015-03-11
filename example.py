from flask import Flask, session, g, redirect, url_for, request
from flask_oauth2 import OAuth2, validate_access, user_loader
from flask.ext.sqlalchemy import SQLAlchemy
from functools import wraps

# Application object
app = Flask('test-oauth2', template_folder='/templates',
            static_folder='/static')

app.config['CSRF_ENABLED'] = True
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'you-will-never-guess-hahahaha :)))))))'
app.config['SERVER_NAME'] = '127.0.0.1:5000'

#flask sqlalchemy
SQLALCHEMY_DATABASE_URI = \
    'mysql+mysqldb://' + \
    'root:nissansunny2005' + \
    '@127.0.0.1/my_project?charset=utf8&use_unicode=0'

app.config['OAUTH2_DATABASE_URI'] =  \
    'mysql+mysqldb://' + \
    'root:nissansunny2005' + \
    '@127.0.0.1/oauth2_server?charset=utf8&use_unicode=0'

app.config['OAUTH2_AUTH_CODE_LENGTH'] = '30'
app.config['OAUTH2_AUTH_URL'] = '/v1/auth'
app.config['OAUTH2_AUTH_EXPIERS_IN'] = '60'  # ms
app.config['OAUTH2_TOKEN_URL'] = '/v1/token'
app.config['OAUTH2_TOKEN_LENGTH'] = '60'
app.config['OAUTH2_TOKEN_EXPIERS_IN'] = '3600'  # ms
app.config['OAUTH2_GRANT_PAGE'] = 'grant.tpl'

db = SQLAlchemy(app)
oauth2 = OAuth2(app, db)

oauth2.register_scope(name='name', description='view your real name')
oauth2.register_scope(name='email', description='view your email')

oauth2.register_client(
    id='123',
    name='imclient',
    description='im client description',
    secret='123321a',
    redirect_uris=[''],
    scopes=['name', 'email']
)

oauth2.grant_client(client_id='123', user_id='1234', scopes=['name', 'email'])


class User(db.model):
    id = db.Column(
        db.String(32), db.ForeignKey('users_human.id'), primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(32), nullable=False)

    def __init__(self, name, email):
        self.id = '123'
        self.name = name
        self.email = email

    def __oauth_id__(self):
        return self.id


@app.before_request
def load_user():
    if 'user_id' in session:
        g.user = User.query.filter_by(id=session['id']).first()


@user_loader
def load_oauth2_user():
    return getattr(g, 'user', None)


def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        user = getattr(g, 'user', None)
        if not user:
            return redirect(url_for('user.login', next=request.url))
        return func(*args, **kwargs)
    return decorated_view


# rotes:
@app.route('/login', methods=['GET', 'POST'])
def login():
    pass


@app.route('/secure', methods=['GET'])
@validate_access(scopes=['name', 'email'])
def secure(user):
    return user.name
