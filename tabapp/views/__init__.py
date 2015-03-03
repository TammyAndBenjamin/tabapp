# -*- coding: utf-8 -*-

from flask import g, render_template
from flask.ext.login import current_user
from flask.ext.babel import (
    format_date, format_datetime, format_time,
    format_currency, format_percent
)
from tabapp.views.supply import supply_bp
from tabapp.views.url import url_bp
from tabapp.views.main import main_bp
from tabapp.views.orders import orders_bp
from tabapp.views.retailers.main import retailers_bp
from tabapp.views.retailers.deliveries import retailers_deliveries_bp
from tabapp.views.retailers.stocks import retailers_stocks_bp
from tabapp.views.products import products_bp
from tabapp.views.users import users_bp
from tabapp.views.roles import roles_bp
from tabapp.views.hooks import hooks_bp
from tabapp.views.admin import admin_bp
from tabapp.views.login import login_bp
from tabapp.views.urls import urls_bp
import tabapp.extensions.security


def init_app(app):
    @app.before_request
    def init_request():
        g.config = app.config
        g.current_user = current_user

    @app.errorhandler(403)
    def page_forbidden(e):
        return render_template('403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def page_error(e):
        return render_template('500.html'), 500

    @app.template_filter('currency')
    def currency_filter(value):
        return format_currency(value, 'EUR')

    @app.template_filter('date')
    def date_filter(date, format=None, locale=None):
        return format_date(date, format, locale)

    @app.template_filter('datetime')
    def datetime_filter(datetime, format=None, locale=None):
        return format_datetime(datetime, format, locale)

    @app.template_filter('time')
    def time_filter(time, format=None, locale=None):
        return format_time(time, format, locale)

    @app.template_filter('percent')
    def percent_filter(value):
        return format_percent(value, '#,##0.##%')

    @app.context_processor
    def utility_processor():
        def can_access(endpoint):
            return tabapp.extensions.security.can_access(endpoint)
        return {'can_access': can_access}

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
    app.register_blueprint(roles_bp, url_prefix='/admin/roles')
    # Data
    app.register_blueprint(supply_bp, url_prefix='/supplies')
    app.register_blueprint(url_bp, url_prefix='/u')
    # Hooks
    app.register_blueprint(hooks_bp)
