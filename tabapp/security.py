# -*- coding: utf-8 -*-

from functools import wraps
from flask import current_app, abort
from flask_wtf.csrf import CsrfProtect
from flask.ext.login import current_user
from flask.ext.principal import (
        Principal,
        identity_loaded,
        RoleNeed,
        UserNeed,
        Permission,
    )
from tabapp.models import Role
import collections


csrf = CsrfProtect()
principals = Principal()


def init_app(app):
    csrf.init_app(app)
    principals.init_app(app)

    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        identity.user = current_user

        if hasattr(current_user, 'id'):
            identity.provides.add(UserNeed(current_user.id))

        if hasattr(current_user, 'roles'):
            for role in current_user.roles:
                identity.provides.add(RoleNeed(role.id))
                for descendant in role.descendants:
                    identity.provides.add(RoleNeed(descendant.id))


def permisssion_required(role_keys):
    if not isinstance(role_keys, collections.Iterable):
        raise
    def decorator(f):
        f.permissions = role_keys
        @wraps(f)
        def decorated_function(*args, **kwargs):
            roles = Role.query.filter(Role.key.in_(role_keys)).all()
            for role in roles:
                permisssion = Permission(RoleNeed(role.id))
                if permisssion.can():
                    return f(*args, **kwargs)
            return abort(403)
        return decorated_function
    return decorator


def can_access(endpoint):
    f = current_app.view_functions[endpoint]
    if not hasattr(f, 'permissions'):
        return True
    roles = Role.query.filter(Role.key.in_(f.permissions)).all()
    for role in roles:
        permisssion = Permission(RoleNeed(role.id))
        if permisssion.can():
            return True
    return False
