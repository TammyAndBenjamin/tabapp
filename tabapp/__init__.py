#!/usr/bin/env python                                                                                                                                                                                                                                                         [98/217]
# -*- coding: utf-8 -*-

from flask import Flask, g, request
from flask_wtf.csrf import CsrfProtect
from flask.ext.login import LoginManager
from flask.ext.babel import Babel


app = Flask(__name__)
app.config.from_pyfile('settings.py')
app.config.from_envvar('SETTINGS')
app.secret_key = app.config['SECRET_KEY']
csrf = CsrfProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_bp.login'


@login_manager.user_loader
def load_user(login_id):
    return Login.query.get(login_id)


from tabapp.models import Login
from tabapp.views import main_bp, orders_bp, retailers_bp,\
    retailers_stocks_bp, users_bp, supply_bp, urls_bp, url_bp, \
    retailers_deliveries_bp, products_bp, hooks_bp, admin_bp, login_bp

# Backyard
app.register_blueprint(main_bp)
app.register_blueprint(login_bp)
app.register_blueprint(orders_bp, url_prefix='/orders')
app.register_blueprint(products_bp, url_prefix='/products')
app.register_blueprint(retailers_bp, url_prefix='/retailers')
app.register_blueprint(retailers_deliveries_bp, url_prefix='/retailers')
app.register_blueprint(retailers_stocks_bp, url_prefix='/retailers')
app.register_blueprint(urls_bp, url_prefix='/urls')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(users_bp, url_prefix='/admin/users')
# Data
app.register_blueprint(supply_bp, url_prefix='/supplies')
app.register_blueprint(url_bp, url_prefix='/u')
# Hooks
app.register_blueprint(hooks_bp)


babel = Babel(app)


@babel.localeselector
def get_locale():
    user = getattr(g, 'user', None)
    if user is not None:
        return user.locale
    return request.accept_languages.best_match(['fr', 'en'])


@babel.timezoneselector
def get_timezone():
    user = getattr(g, 'user', None)
    if user is not None:
        return user.timezone
