# -*- coding: utf-8 -*-

from tabapp import app
from flask import g
from flask.ext.login import current_user
from flask.ext.babel import format_date, format_datetime, format_time,\
    format_currency, format_percent


@app.before_request
def init_request():
    g.config = app.config
    g.current_user = current_user


@app.template_filter('currency')
def currency_filter(value):
    return format_currency(value, 'EUR')


@app.template_filter('date')
def date_filter(date, format = None, locale = None):
    return format_date(date, format, locale)


@app.template_filter('datetime')
def datetime_filter(datetime, format = None, locale = None):
    return format_datetime(datetime, format, locale)


@app.template_filter('time')
def time_filter(time, format = None, locale = None):
    return format_time(time, format, locale)


@app.template_filter('percent')
def percent_filter(value):
    return format_percent(value)


from tabapp.views.main import main_bp
from tabapp.views.orders import orders_bp
from tabapp.views.retailers import retailers_bp
from tabapp.views.retailers_deliveries import retailers_deliveries_bp
from tabapp.views.retailers_stocks import retailers_stocks_bp
from tabapp.views.products import products_bp
from tabapp.views.users import users_bp
from tabapp.views.supply import supply_bp
from tabapp.views.hooks import hooks_bp
from tabapp.views.admin import admin_bp
