# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request, abort, current_app
from flask.ext.babel import gettext as _
from tabapp.security import permisssion_required
from tabapp.models import db, Contact
from tabapp.forms import ContactForm, CredentialsForm

users_bp = Blueprint('users_bp', __name__, subdomain='backyard')


@users_bp.route('/')
@permisssion_required(['admin'])
def list():
    contacts = Contact.query.all()
    context = {
        'contacts': contacts,
    }
    return render_template('admin/users/list.html', **context)


@users_bp.route('/new', defaults={'user_id': None}, methods=['GET', 'POST'])
@users_bp.route('/<int:user_id>', methods=['GET', 'POST'])
@permisssion_required(['admin'])
def user(user_id):
    contact = Contact.query.get(user_id) if user_id else Contact()
    contact_form = ContactForm(obj=contact)
    credentials_form = CredentialsForm(obj=contact)
    forms = {
        'contact_details': contact_form,
        'contact_credentials': credentials_form,
    }
    current_form = forms.get(request.form.get('action'))
    if current_form and current_form.validate_on_submit():
        contact = Contact.query.get(user_id) if user_id else Contact()
        current_app.logger.debug(str(contact.password))
        current_form.populate_obj(contact)
        current_app.logger.debug(str(contact.password))
        if current_form is contact_form:
            contact.phone = current_form.phone.data
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
        'contact_form': contact_form,
        'credentials_form': credentials_form,
    }
    return render_template('admin/users/form.html', **context)


@users_bp.route('/<int:user_id>', methods=['DELETE'])
@permisssion_required(['admin'])
def delete(user_id):
    contact = Contact.query.get(user_id)
    if not contact:
        return abort(404)
    db.session.delete(contact)
    db.session.commit()
    return jsonify(redirect=url_for('users_bp.list'))
