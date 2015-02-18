#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from tabapp import models, auth, security, lang, views


def create_app():
    """ Initialize app and all the modules """
    app = Flask(__name__)
    app.config.from_pyfile('settings.py')
    app.config.from_envvar('SETTINGS')
    app.secret_key = app.config['SECRET_KEY']

    models.db.app = app
    models.db.init_app(app)
    security.init_app(app)
    auth.login_manager.init_app(app)
    lang.init_app(app)
    views.init_app(app)

    return app
