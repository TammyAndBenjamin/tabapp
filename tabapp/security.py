# -*- coding: utf-8 -*-

from functools import wraps
from flask import redirect, request, url_for, current_app
from flask_wtf.csrf import CsrfProtect
from flask.ext.login import current_user
from flask.ext.principal import (
        Principal,
        identity_loaded,
        RoleNeed,
        UserNeed,
        Permission,
        PermissionDenied,
    )
from tabapp.models import Role


csrf = CsrfProtect()
principals = Principal()


def init_app(app):
    csrf.init_app(app)
    principals.init_app(app)

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
            for role_id in current_user.roles:
                identity.provides.add(RoleNeed(role_id))


def permisssion_required(role_keys):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            role = Role.query.filter(Role.key.in_(role_keys)).first()
            permisssion = Permission(RoleNeed(role.id))
            try:
                with permisssion.require():
                    return f(*args, **kwargs)
            except PermissionDenied:
                return redirect(url_for('login_bp.login', next=request.url))
        return decorated_function
    return decorator
