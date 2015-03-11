from flask import current_app
from flask import _app_ctx_stack as stack
from flask import Flask
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import datetime
import os

basedir = os.path.abspath(os.path.dirname(__file__))

#set up sqlalchemy
engine = create_engine('sqlite:///' + os.path.join(basedir, 'oauth2.db'))
Base = declarative_base()
metadata = Base.metadata
metadata.bind = engine
Session = sessionmaker(bind=engine, autoflush=True)
session = Session()

class OAuth2(object):

    def __init__(self, app=None):
        if app is not None:
            self.app = app
            self.init_app(app)
        else:
            self.app = None
        metadata.create_all()

    def init_app(self, app):
        app.teardown_appcontext(self.teardown)

    def teardown(self, exception):
        """
        This will close the database after each request that uses oauth2
        """
        pass

    def register_scope(self,
                       scope,
                       description):
        scope = Scope(scope, description)
        session.add(scope)
        session.commit()

    def get_scope(self, id=None, scope=None):
        if id is not None and scope is None:
            scope = session.query(Scope).filter_by(id=id).first()
            return scope
        elif scope is not None and id is None:
            scope = session.query(Scope).filter_by(scope=scope).first()
            return scope
        else:
            return None

# Models
class Scope(Base):
    __tablename__ = 'oauth2_scopes'
    id = Column(String(32), primary_key=True)
    scope =Column(String(20), nullable=False)
    description = Column(String(200))

    def __init__(self, scope, description):
        self.id = generate_uuid4()
        self.scope = scope
        self.description = description


# utils
from uuid import uuid4

def generate_uuid4():
    """
    generates UUID4 without dashes (-)
    """
    return unicode(uuid4()).replace('-', '')
