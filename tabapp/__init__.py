#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from tabapp import auth, models, lang, views, security


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('settings.py')
    app.config.from_envvar('SETTINGS')
    app.secret_key = app.config['SECRET_KEY']

    models.db.init_app(app)
    auth.login_manager.init_app(app)
    lang.init_app(app)
    security.csrf.init_app(app)
    views.init_app(app)

    return app
