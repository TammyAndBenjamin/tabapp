# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, g, current_app, abort
from tabapp.models import db, Contact

admin_bp = Blueprint('admin_bp', __name__, subdomain='backyard')


@admin_bp.route('/')
def index():
    return render_template('admin/index.html')


@admin_bp.route('/users/')
def users():
    users = Contact.query.all()
    context = {
        'users': users,
    }
    return render_template('admin/users.html', **context)
