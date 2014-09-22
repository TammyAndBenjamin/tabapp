# -*- coding: utf-8 -*-

from flask import Blueprint, request, render_template, g, redirect, url_for, flash, current_app
from flask.ext.login import login_required, logout_user, login_user
import hashlib
import psycopg2.extras

users_bp = Blueprint('users_bp', __name__, subdomain='backyard')


@users_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    username = request.form.get('username')
    salted_password = g.config['SECRET_KEY'] + request.form.get('password')
    hashed_password = hashlib.md5(salted_password.encode('ascii'))
    user = db.Login.query.filter_by(username=username, password=hashed_password.hexdigest()).first()
    if not user:
        return render_template('login.html')
    login_user(user)
    return redirect(request.args.get('next') or url_for('index'))


@users_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
