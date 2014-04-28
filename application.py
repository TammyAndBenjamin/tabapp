#!/usr/bin/env python                                                                                                                                                                                                                                                         [98/217]
# -*- coding: utf-8 -*-

from flask import Flask, request, render_template, jsonify, g
from flask.ext.httpauth import HTTPBasicAuth
from flask_wtf.csrf import CsrfProtect
from orders import orders_bp
import json


app = Flask(__name__)
app.config.from_pyfile('settings.py')
app.secret_key = app.config['SECRET_KEY']
app.register_blueprint(orders_bp, url_prefix='/orders')
CsrfProtect(app)
app.auth = HTTPBasicAuth()

@app.before_request
def init_request():
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
