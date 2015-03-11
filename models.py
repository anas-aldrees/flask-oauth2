

class Scope(OAuth2.db.Model):
    __tablename__ = 'oauth2_scopes'
    id = OAuth2.db.Column(OAuth2.db.String(32), primary_key=True)
    scope =OAuth2.db.Column(OAuth2.db.String(20), nullable=False)
    description = OAuth2.db.Column(OAuth2.db.String(200))

    def __init__(self, scope, description):
        self.id = generate_uuid4()
        self.scope = scope
        self.description = description

class ClientRedirectUri(OAuth2.db.Model):
    __tablename__ = 'oauth2_clients_redirect_uris'

    client_id = OAuth2.db.Column('client_id', OAuth2.db.String(30),
                       OAuth2.db.ForeignKey('oauth2_clients.id'),
                       primary_key=True)
    client = OAuth2.db.relationship('Client')
    redirect_uri = OAuth2.db.Column('redirect_uri',
                          OAuth2.db.String(200),
                          nullable=False,
                          primary_key=True)

    def __init__(self, client, redirect_uri):
        self.client = client
        self.redirect_uri = redirect_uri

clients_scopes = OAuth2.db.Table('oauth2_client_scopes', OAuth2.db.metadata,
                       OAuth2.db.Column('client_id',
                              OAuth2.db.String(32),
                              OAuth2.db.ForeignKey('oauth2_clients.id',
                                         ondelete='CASCADE',
                                         onupdate='CASCADE'),
                              nullable=False),
                       OAuth2.db.Column('scope_id',
                              OAuth2.db.String(32),
                              OAuth2.db.ForeignKey('oauth2_scopes.id',
                                         ondelete='CASCADE',
                                         onupdate='CASCADE'),
                              nullable=False
                              )
                       )

class Client(OAuth2.db.Model):
    __tablename__ = 'oauth2_clients'

    id = OAuth2.db.Column(OAuth2.db.String(30), primary_key=True)
    name = OAuth2.db.Column(OAuth2.db.String(100), nullable=False)
    description = OAuth2.db.Column(OAuth2.db.Text, nullable=True)
    secret = OAuth2.db.Column(OAuth2.db.String(20), nullable=False)
    redirect_uris = OAuth2.db.relationship(ClientRedirectUri)
    scopes = OAuth2.db.relationship("Scope",
                          secondary=clients_scopes)
    is_allowed = OAuth2.db.Column(OAuth2.db.Boolean, default=False)

    def __init__(self, client_id, name, description, secret):
        self.id = client_id
        self.name = name
        self.description = description
        self.secret = secret
