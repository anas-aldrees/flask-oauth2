from oauthh import db
from oauthh.oauth2.m.client_redirect_uri import ClientRedirectUri


clients_scopes = db.Table('oauth2_client_scopes', db.metadata,
                       db.Column('client_id',
                              db.String(32),
                              db.ForeignKey('oauth2_clients.id',
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


class Client(db.Model):
    __tablename__ = 'oauth2_clients'

    id = db.Column(db.String(30), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    secret = db.Column(db.String(20), nullable=False)
    redirect_uris = db.relationship(ClientRedirectUri)
    scopes = db.relationship("Scope",
                          secondary=clients_scopes)
    is_allowed = db.Column(db.Boolean, default=False)

    def __init__(self, client_id, name, description, secret):
        self.id = client_id
        self.name = name
        self.description = description
        self.secret = secret
