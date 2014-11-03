# -*- coding: utf-8 -*-

from flask import Blueprint, request, render_template, g, redirect, url_for, flash, current_app
from flask.ext.login import login_required, logout_user, login_user
from flask.ext.babel import gettext as _
from tabapp.models import db, Login, Contact
from tabapp.forms import ContactForm

users_bp = Blueprint('users_bp', __name__, subdomain='backyard')


@users_bp.route('/users/')
def list():
    users = Contact.query.all()
    context = {
        'users': users,
    }
    return render_template('admin/users/list.html', **context)


@users_bp.route('/users/new')
def new():
    form = ContactForm()
    context = {
        'user_id': None,
        'form': form,
    }
    return render_template('admin/users/form.html', **context)


@users_bp.route('/users/<int:user_id>', methods=['GET', 'POST'])
def user(user_id):
    form = None
    if request.method == 'POST':
        form = ContactForm(request.form)
        if form.validate():
            contact = Contact.query.get(user_id)\
                if user_id else Contact()
            form.populate_obj(contact)
            if not contact.id:
                db.session.add(contact)
            db.session.commit()
            flash(_('User updated.'), 'success')
            kwargs = {
                'user_id': contact.id,
            }
            return redirect(url_for('users_bp.user', **kwargs))
    contact = Contact.query.get(user_id) if user_id else Contact()
    form = ContactForm(obj=contact) if not form else form
    context = {
        'user_id': contact.id,
        'form': form,
    }
    return render_template('admin/users/form.html', **context)


@users_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form.get('username')
    password = request.form.get('password')
    login = Login.query.filter(Login.username==username).first()
    if not login or login.password != password:
        flash(_('Unknown user'), 'error')
        return render_template('login.html')
    login_user(login)
    return redirect(request.args.get('next') or url_for('index'))


@users_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main_bp.index'))
