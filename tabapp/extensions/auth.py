# -*- coding: utf-8 -*-

from flask_login import LoginManager
from tabapp.models import Contact


login_manager = LoginManager()
login_manager.login_view = 'login_bp.login'


@login_manager.user_loader
def load_user(contact_id):
    return Contact.query.get(contact_id)
