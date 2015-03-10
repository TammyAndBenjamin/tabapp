# -*- coding: utf-8 -*-

from flask import Blueprint, request, render_template, g, redirect, url_for, flash, current_app, session
from flask_login import login_required, logout_user, login_user
from flask_babel import gettext as _
from flask_principal import Identity, AnonymousIdentity, identity_changed
from tabapp.models import Contact

login_bp = Blueprint('login_bp', __name__, subdomain='backyard')


@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form.get('username')
    password = request.form.get('password')
    contact = Contact.query.filter(Contact.username == username).first()
    if not contact or contact.password != password:
        flash(_('Unknown user'), 'error')
        return render_template('login.html')
    login_user(contact)
    identity_changed.send(current_app._get_current_object(), identity=Identity(contact.id))
    return redirect(request.args.get('next') or url_for('index'))


@login_bp.route('/logout')
@login_required
def logout():
    logout_user()
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())
    return redirect(url_for('main_bp.index'))
