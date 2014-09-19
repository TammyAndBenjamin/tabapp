# -*- coding: utf-8 -*-

from flask import Blueprint, request, render_template, g, redirect, url_for, flash, current_app
from flask.ext.login import login_required, logout_user, login_user
from user import User
import psycopg2.extras

users_bp = Blueprint('users_bp', __name__, subdomain='backyard')


@users_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('''
        SELECT *
        FROM login
        WHERE username = %s
        AND password = %s
    ''', (request.form.get('username'), request.form.get('password')))
    row = cur.fetchone()
    if not row:
        return render_template('login.html')
    user = User(row)
    login_user(user)
    return redirect(request.args.get('next') or url_for('index'))


@users_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
