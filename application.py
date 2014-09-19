#!/usr/bin/env python                                                                                                                                                                                                                                                         [98/217]
# -*- coding: utf-8 -*-

from flask import Flask, render_template, g
from flask_wtf.csrf import CsrfProtect
from flask.ext.login import LoginManager, login_required
from orders import orders_bp
from product_costs import product_costs_bp
from retailers import retailers_bp
from users import users_bp
from supply import supply_bp
from user import User
import psycopg2


app = Flask(__name__)
app.db = None
app.config.from_pyfile('settings.py')
app.secret_key = app.config['SECRET_KEY']
app.register_blueprint(orders_bp, url_prefix='/orders')
app.register_blueprint(product_costs_bp, url_prefix='/products_costs')
app.register_blueprint(retailers_bp, url_prefix='/retailers')
app.register_blueprint(users_bp, url_prefix='/login')
app.register_blueprint(supply_bp, url_prefix='/supplies')
CsrfProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users_bp.login'


@login_manager.user_loader
def load_user(userid):
    cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('''
        SELECT *
        FROM login
        WHERE id = %s
    ''', (userid,))
    row = cur.fetchone()
    if not row:
        return None
    return User(row)


@app.before_request
def init_request():
    if not app.db:
        app.db = psycopg2.connect(host=app.config['DB_HOST'], user=app.config['DB_USER'], dbname=app.config['DB_NAME'])
        app.db.autocommit = True
    g.db = app.db
    g.config = app.config


@app.route('/', subdomain='backyard')
@login_required
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host='62.210.207.214', port=5050, debug=True)
