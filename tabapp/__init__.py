#!/usr/bin/env python                                                                                                                                                                                                                                                         [98/217]
# -*- coding: utf-8 -*-

from flask import Flask, render_template, g
from flask_wtf.csrf import CsrfProtect
from flask.ext.login import LoginManager, login_required, current_user


app = Flask(__name__)
app.config.from_pyfile('settings.py')
app.secret_key = app.config['SECRET_KEY']
csrf = CsrfProtect(app)

from tabapp.models import Login
from tabapp.views import main_bp, orders_bp, retailers_bp,\
    retailers_supplies_bp, users_bp, supply_bp, products_bp, hooks_bp

# Backyard
app.register_blueprint(main_bp)
app.register_blueprint(orders_bp, url_prefix='/orders')
app.register_blueprint(products_bp, url_prefix='/products')
app.register_blueprint(retailers_bp, url_prefix='/retailers')
app.register_blueprint(retailers_supplies_bp, url_prefix='/retailers')
app.register_blueprint(users_bp, url_prefix='/login')
# Data
app.register_blueprint(supply_bp, url_prefix='/supplies')
# Hooks
app.register_blueprint(hooks_bp)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users_bp.login'


@login_manager.user_loader
def load_user(userid):
    return Login.query.get(userid)


@app.before_request
def init_request():
    g.config = app.config
    g.current_user = current_user


@app.template_filter('currency')
def currency_filter(s):
    return '{:.2f} €'.format(s)
