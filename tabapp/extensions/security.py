# -*- coding: utf-8 -*-

from functools import wraps
from flask import current_app, abort, redirect, url_for, request
from flask_wtf.csrf import CsrfProtect
from flask_login import current_user
from flask_principal import (
        Principal,
        identity_loaded,
        RoleNeed,
        UserNeed,
        ItemNeed,
        Permission,
    )
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
                identity.provides.add(RoleNeed(role.key))
                for descendant in role.descendants:
                    identity.provides.add(RoleNeed(descendant.key))

        if hasattr(current_user, 'retailers'):
            for retailer in current_user.retailers:
                identity.provides.add(ItemNeed('access', 'retailer', retailer.id))


def permisssion_required(role_keys):
    if not isinstance(role_keys, collections.Iterable):
        raise
    def decorator(f):
        f.role_keys = role_keys
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated():
                return redirect(url_for('login_bp.login', next=request.path))
            for key in role_keys:
                permisssion = Permission(RoleNeed(key))
                if permisssion.can():
                    return f(*args, **kwargs)
            return abort(403)
        return decorated_function
    return decorator


def can_access(endpoint):
    """ Method used in templates only, it helps to validate endpoint access """
    f = current_app.view_functions[endpoint]
    if not hasattr(f, 'role_keys'):
        return True
    for role_key in f.role_keys:
        permisssion = Permission(RoleNeed(role_key))
        if permisssion.can():
            return True
    return False
