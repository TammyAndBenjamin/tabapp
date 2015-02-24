# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, redirect, url_for, flash, abort, jsonify
from flask.ext.babel import gettext as _
from tabapp.security import permisssion_required
from tabapp.models import db, Role
from tabapp.forms import RoleForm

roles_bp = Blueprint('roles_bp', __name__, subdomain='backyard')


@roles_bp.route('/')
@permisssion_required(['admin'])
def list():
    roles = Role.query.all()
    descendants = {}
    for role in roles:
        descendants[role.id] = [descendant.name for descendant in role.descendants]
    context = {
        'roles': roles,
        'descendants': descendants,
    }
    return render_template('admin/roles/list.html', **context)


@roles_bp.route('/new', defaults={'role_id': None}, methods=['GET', 'POST'])
@roles_bp.route('/<int:role_id>', methods=['GET', 'POST'])
@permisssion_required(['admin'])
def role(role_id):
    role = Role.query.get(role_id) if role_id else Role()
    form = RoleForm(obj=role)
    form.roles.query = Role.query.filter(Role.id != role.id)
    if form.validate_on_submit():
        form.populate_obj(role)
        if not role.id:
            db.session.add(role)
        db.session.commit()
        flash(_('Role updated.'), 'success')
        kwargs = {
            'role_id': role.id,
        }
        return redirect(url_for('roles_bp.role', **kwargs))
    context = {
        'role_id': role.id,
        'form': form,
    }
    return render_template('admin/roles/form.html', **context)


@roles_bp.route('/<int:role_id>', methods=['DELETE'])
@permisssion_required(['admin'])
def delete(role_id):
    role = Role.query.get(role_id)
    if not role:
        return abort(404)
    db.session.delete(role)
    db.session.commit()
    return jsonify(redirect=url_for('roles_bp.list'))
