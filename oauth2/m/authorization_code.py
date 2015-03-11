from oauthh import db
from lib.util import generate_uuid4


authorization_codes_scopes = db.Table('oauth2_authorization_codes_scopes',
                                   db.metadata,
                                   db.Column('authorization_code_id',
                                          db.String(32),
                                          db.ForeignKey(
                                              'oauth2_authorization_codes.id',
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


class AuthorizationCode(db.Model):
    __tablename__ = 'oauth2_authorization_codes'

    id = db.Column(db.String(32), primary_key=True)
    client_id = db.Column(db.String(32), db.ForeignKey('oauth2_clients.id'))
    client = db.relationship('Client')
    user_id = db.Column(db.String(32), db.ForeignKey('user_users.id'))
    user = db.relationship('User')
    code = db.Column(db.String(60), nullable=False)
    date_time = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP'))
    scopes = db.relationship("Scope",
                          secondary=authorization_codes_scopes)

    def __init__(self, client_id, user_id, code, scopes):
        self.id = generate_uuid4()
        self.client_id = client_id
        self.user_id = user_id
        self.code = code
        self.scopes = scopes
