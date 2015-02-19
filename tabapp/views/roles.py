# -*- coding: utf-8 -*-

from flask import Blueprint, render_template
from flask.ext.babel import gettext as _
from tabapp.security import permisssion_required
from tabapp.models import Role

roles_bp = Blueprint('roles_bp', __name__, subdomain='backyard')


@roles_bp.route('/')
@permisssion_required(['admin'])
def list():
    roles = Role.query.all()
    context = {
        'roles': roles,
    }
    return render_template('admin/roles/list.html', **context)


@roles_bp.route('/new', defaults={'role_id': None}, methods=['GET', 'POST'])
@roles_bp.route('/<int:role_id>', methods=['GET', 'POST'])
@permisssion_required(['admin'])
def role(role_id):
    roles = Role.query.all()
    context = {
        'roles': roles,
    }
    return render_template('admin/roles/list.html', **context)
