#!/usr/bin/env python                                                                                                                                                                                                                                                         [98/217]
# -*- coding: utf-8 -*-

from flask import Flask, render_template, g
from flask_wtf.csrf import CsrfProtect
from flask.ext.login import LoginManager, login_required
from flask.ext.sqlalchemy import SQLAlchemy
import psycopg2


app = Flask(__name__)
app.db = None
app.config.from_pyfile('settings.py')
app.secret_key = app.config['SECRET_KEY']
CsrfProtect(app)

db = SQLAlchemy(app)

from tabapp.models import Login
from tabapp.views.main import main_bp
from tabapp.views.orders import orders_bp
from tabapp.views.product_costs import product_costs_bp
from tabapp.views.retailers import retailers_bp
from tabapp.views.users import users_bp
from tabapp.views.supply import supply_bp

app.register_blueprint(main_bp)
app.register_blueprint(orders_bp, url_prefix='/orders')
app.register_blueprint(product_costs_bp, url_prefix='/products_costs')
app.register_blueprint(retailers_bp, url_prefix='/retailers')
app.register_blueprint(users_bp, url_prefix='/login')
app.register_blueprint(supply_bp, url_prefix='/supplies')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users_bp.login'


@login_manager.user_loader
def load_user(userid):
    return Login.query.get(userid)


@app.before_request
def init_request():
    g.config = app.config
