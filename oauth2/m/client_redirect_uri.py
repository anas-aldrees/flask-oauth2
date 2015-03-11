from oauthh import db

class ClientRedirectUri(db.Model):
    __tablename__ = 'oauth2_clients_redirect_uris'

    client_id = db.Column('client_id', db.String(30),
                       db.ForeignKey('oauth2_clients.id'),
                       primary_key=True)
    client = db.relationship('Client')
    redirect_uri = db.Column('redirect_uri',
                          db.String(200),
                          nullable=False,
                          primary_key=True)

    def __init__(self, client, redirect_uri):
        self.client = client
        self.redirect_uri = redirect_uri
