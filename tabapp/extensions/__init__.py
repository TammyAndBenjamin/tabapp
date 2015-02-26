# -*- coding: utf-8 -*-

from tabapp.models import db
from tabapp.extensions import auth, security, lang
from tabapp.extensions.migrate import migrate

def init(app):
    security.init_app(app)
    auth.login_manager.init_app(app)
    lang.init_app(app)
    migrate.init_app(app, db)
