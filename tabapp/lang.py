# -*- coding: utf-8 -*-

from flask import request, g
from flask.ext.babel import Babel


babel = Babel()


def init_app(app):
    babel.init_app(app)

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
