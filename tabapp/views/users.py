# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, g, redirect, url_for, flash
from flask.ext.login import login_required
from flask.ext.babel import gettext as _
from tabapp.models import db, Contact
from tabapp.forms import ContactForm

users_bp = Blueprint('users_bp', __name__, subdomain='backyard')


@users_bp.route('/')
@login_required
def list():
    contacts = Contact.query.all()
    context = {
        'contacts': contacts,
    }
    return render_template('admin/users/list.html', **context)


@users_bp.route('/new', defaults={'user_id': None}, methods=['GET', 'POST'])
@users_bp.route('/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user(user_id):
    contact = Contact.query.get(user_id) if user_id else Contact()
    form = ContactForm(obj=contact)
    if form.validate_on_submit():
        contact = Contact.query.get(user_id)\
            if user_id else Contact()
        form.populate_obj(contact)
        contact.phone = form.phone.data
        if not contact.id:
            db.session.add(contact)
        db.session.commit()
        flash(_('User updated.'), 'success')
        kwargs = {
            'user_id': contact.id,
        }
        return redirect(url_for('users_bp.user', **kwargs))
    context = {
        'user_id': contact.id,
        'contact': contact,
        'form': form,
    }
    return render_template('admin/users/form.html', **context)
