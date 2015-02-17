#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from tabapp import auth, models, lang, views, security
from flask.ext.login import current_user
from flask.ext.principal import Principal, identity_loaded, RoleNeed, UserNeed, Permission


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

principals = Principal()
principals.init_app(app)

admin_permission = Permission(RoleNeed('admin'))


@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    # Set the identity user object
    identity.user = current_user

    # Add the UserNeed to the identity
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))

    # Assuming the User model has a list of roles, update the
    # identity with the roles that the user provides
    if hasattr(current_user, 'roles'):
        for role in current_user.roles:
            identity.provides.add(RoleNeed(role.name))
