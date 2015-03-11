from oauthh import db
from lib.util import generate_uuid4

tokens_scopes = db.Table('oauth2_tokens_scopes',
                      db.metadata,
                      db.Column('token_id',
                             db.String(32),
                             db.ForeignKey('oauth2_tokens.id',
                                        ondelete='CASCADE',
                                        onupdate='CASCADE'),
                             nullable=False),
                      db.Column('scope_id',
                             db.String(32),
                             db.ForeignKey('oauth2_scopes.id',
                                        ondelete='CASCADE',
                                        onupdate='CASCADE'),
                             nullable=False
                             )
                      )


class Token(db.Model):
    __tablename__ = 'oauth2_tokens'
    id = db.Column(db.String(32), primary_key=True)
    client_id = db.Column(db.String(32), db.ForeignKey('oauth2_clients.id'))
    client = db.relationship('Client')
    user_id = db.Column(db.String(32), db.ForeignKey('user_users.id'))
    user = db.relationship('User')
    access_token = db.Column(db.String(60), nullable=False, unique=True)
    token_type = db.Column(db.String(20), nullable=False)
    expires_in = db.Column(db.SmallInteger, nullable=False)
    refresh_token = db.Column(db.String(60), nullable=False, unique=True)
    date_time = db.Column(db.TIMESTAMP,
                       server_default=db.text('CURRENT_TIMESTAMP'),
                       nullable=False, onupdate=db.text('CURRENT_TIMESTAMP'))
    scopes = db.relationship('Scope',
                          secondary=tokens_scopes)

    def __init__(self, client_id, user_id, access_token,
                 token_type, expires_in, refresh_token, scopes):
        self.id = generate_uuid4()
        self.client_id = client_id
        self.user_id = user_id
        self.access_token = access_token
        self.token_type = token_type
        self.expires_in = expires_in
        self.refresh_token = refresh_token
        self.scopes = scopes
