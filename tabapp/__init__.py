#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from tabapp import views, extensions
from tabapp.models import db


def create_app():
    """ Initialize app and all the modules """
    app = Flask(__name__)
    app.config.from_pyfile('settings.py')
    app.config.from_envvar('SETTINGS')
    app.secret_key = app.config['SECRET_KEY']

    db.init_app(app)
    views.init_app(app)
    extensions.init(app)

    return app
