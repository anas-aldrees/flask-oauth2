from oauthh import db
from lib.util import generate_uuid4


class Scope(db.Model):
    __tablename__ = 'oauth2_scopes'
    id = db.Column(db.String(32), primary_key=True)
    scope = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(200))

    def __init__(self, scope, description):
        self.id = generate_uuid4()
        self.scope = scope
        self.description = description
