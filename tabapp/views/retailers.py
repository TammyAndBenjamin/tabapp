# -*- coding: utf-8 -*-

from datetime import date
from flask import Blueprint, request, render_template, redirect,\
    url_for, flash, jsonify, abort
from flask.ext.login import login_required
from tabapp.models import db, Retailer, RetailerProduct
from tabapp.forms import RetailerForm
import tabapp.utils


retailers_bp = Blueprint('retailers_bp', __name__, subdomain='backyard')


def tab_counts(retailer):
    counts = {
        'supplies': RetailerProduct.query.filter(
            RetailerProduct.retailer_id == retailer.id,
            RetailerProduct.sold_date.is_(None)
        ).count(),
        'sold': RetailerProduct.query.filter(
            RetailerProduct.retailer_id == retailer.id,
            RetailerProduct.sold_date.isnot(None)
        ).count(),
        'invoices': RetailerProduct.query.filter(
            RetailerProduct.retailer_id == retailer.id,
            RetailerProduct.payment_date.isnot(None)
        ).count(),
    }
    return counts


@retailers_bp.route('/')
@login_required
def index():
    retailers = Retailer.query.all()
    context = {
        'retailers': retailers,
    }
    return render_template('retailers/index.html', **context)


@retailers_bp.route('/<int:retailer_id>/', methods=['GET'])
@login_required
def retailer(retailer_id):
    retailer = Retailer.query.get(retailer_id)
    if not retailer:
        return abort(404)
    context = {
        'retailer': retailer,
        'tab_counts': tab_counts(retailer),
    }
    return render_template('retailers/retailer.html', **context)


@retailers_bp.route('/new')
@login_required
def new_retailer():
    form = RetailerForm()
    context = {
        'retailer_id': None,
        'form': form,
    }
    return render_template('retailers/form.html', **context)


@retailers_bp.route('/', defaults={'retailer_id': None}, methods=['POST'])
@retailers_bp.route('/<int:retailer_id>/', methods=['POST'])
@retailers_bp.route('/<int:retailer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_retailer(retailer_id):
    form = None
    if request.method == 'POST':
        form = RetailerForm(request.form)
        if form.validate():
            retailer = Retailer.query.get(retailer_id)\
                if retailer_id else Retailer()
            retailer.name = form.name.data
            retailer.fees_proportion = form.fees_proportion.data / 100
            retailer.address = form.address.data
            if not retailer.id:
                db.session.add(retailer)
            db.session.commit()
            flash('Retailer updated.', 'success')
            kwargs = {
                retailer_id: retailer.id,
            }
            return redirect(url_for('retailers_bp.retailer', **kwargs))
    retailer = Retailer.query.get(retailer_id) if retailer_id else Retailer()
    form = RetailerForm(obj=retailer) if not form else form
    form.fees_proportion.data = form.fees_proportion.data * 100\
        if form.fees_proportion.data else 0
    context = {
        'retailer_id': retailer.id,
        'form': form,
    }
    return render_template('retailers/form.html', **context)


@retailers_bp.route('/<int:retailer_id>/', methods=['DELETE'])
@retailers_bp.route('/<int:retailer_id>/delete', methods=['POST'])
@login_required
def delete_retailer(retailer_id):
    retailer = Retailer.query.get(retailer_id)
    if not retailer:
        return abort(404)
    db.session.delete(retailer)
    db.session.commit()
    if tabapp.utils.request_wants_json():
        return jsonify(success='Retailer deleted.')
    flash('Retailer deleted.', 'success')
    return redirect(url_for('retailers_bp.index'))


@retailers_bp.route('/<int:retailer_id>/sold/', methods=['GET', 'POST'])
@login_required
def sold(retailer_id):
    retailer = Retailer.query.get(retailer_id)
    if not retailer:
        return abort(404)
    if request.method == 'POST':
        pass
    context = {
        'retailer': retailer,
        'tab_counts': tab_counts(retailer),
    }
    return render_template('retailers/sold.html', **context)


@retailers_bp.route('/<int:retailer_id>/invoices/', methods=['GET'])
@login_required
def invoices(retailer_id):
    retailer = Retailer.query.get(retailer_id)
    context = {
        'retailer': retailer,
    }
    return render_template('retailers/invoices.html', **context)
