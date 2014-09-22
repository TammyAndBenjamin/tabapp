#!/usr/bin/env python                                                                                                                                                                                                                                                         [98/217]
# -*- coding: utf-8 -*-

from flask import Flask, render_template, g
from flask_wtf.csrf import CsrfProtect
from flask.ext.login import LoginManager, login_required
from flask.ext.sqlalchemy import SQLAlchemy
from orders import orders_bp
from product_costs import product_costs_bp
from retailers import retailers_bp
from users import users_bp
from supply import supply_bp
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

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users_bp.login'


class Login(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, index = True, unique = True)
    password = db.Column(db.String)

    def is_authenticated(self):
        return bool(self.id)


    def is_active(self):
        return bool(self.id)


    def is_anonymous(self):
        return not bool(self.id)


    def get_id(self):
        return str(self.id)


@login_manager.user_loader
def load_user(userid):
    return Login.query.get(userid)


@app.before_request
def init_request():
    g.db = db
    g.config = app.config


@app.route('/', subdomain='backyard')
@login_required
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host='62.210.207.214', port=5050, debug=True)
