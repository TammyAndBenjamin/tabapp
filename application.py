#!/usr/bin/env python                                                                                                                                                                                                                                                         [98/217]
# -*- coding: utf-8 -*-

from flask import Flask, request, render_template, g
from flask.ext.httpauth import HTTPBasicAuth
from flask_wtf.csrf import CsrfProtect
from orders import orders_bp
from product_costs import product_costs_bp
from supply import supply_bp
import json
import psycopg2


app = Flask(__name__)
app.db = None
app.config.from_pyfile('settings.py')
app.secret_key = app.config['SECRET_KEY']
app.register_blueprint(orders_bp, url_prefix='/orders')
app.register_blueprint(product_costs_bp, url_prefix='/products_costs')
app.register_blueprint(supply_bp, url_prefix='/supply')
CsrfProtect(app)
app.auth = HTTPBasicAuth()

@app.before_request
def init_request():
    if not app.db:
        app.db = psycopg2.connect(host=app.config['DB_HOST'], user=app.config['DB_USER'], dbname=app.config['DB_NAME'])
        app.db.autocommit = True
    g.db = app.db
    g.config = app.config

@app.auth.get_password
def get_pw(username):
    if username in app.config['USERS']:
        return app.config['USERS'].get(username)
    return None

@app.route('/')
@app.auth.login_required
def index():
    return render_template('index.html')

@app.route('/analytics')
@app.auth.login_required
def analytics():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host='62.210.207.214', port=5050, debug=True)
