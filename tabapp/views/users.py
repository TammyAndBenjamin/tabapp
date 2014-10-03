# -*- coding: utf-8 -*-

from flask import Blueprint, request, render_template, g, redirect, url_for, flash, current_app
from flask.ext.login import login_required, logout_user, login_user
from tabapp.models import db, Login

users_bp = Blueprint('users_bp', __name__, subdomain='backyard')


@users_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form.get('username')
    password = request.form.get('password')
    login = db.session.query(Login).filter(username==username, password==password).first()
    if not login:
        return render_template('login.html')
    login_user(login)
    return redirect(request.args.get('next') or url_for('index'))


@users_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main_bp.index'))
