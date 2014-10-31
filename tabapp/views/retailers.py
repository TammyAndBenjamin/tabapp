# -*- coding: utf-8 -*-

from datetime import date
from flask import Blueprint, request, render_template, redirect,\
    url_for, flash, jsonify, abort, current_app, g
from flask.ext.login import login_required
from tabapp.models import db, Invoice, InvoiceItem, Retailer,\
    RetailerProduct, DeliverySlip
from tabapp.forms import RetailerForm
import tabapp.utils
import decimal
import sqlalchemy
import sqlalchemy.dialects.postgresql


retailers_bp = Blueprint('retailers_bp', __name__, subdomain='backyard')


def tab_counts(retailer):
    counts = {
        'delivery_slips': DeliverySlip.query.filter(
            DeliverySlip.retailer_id == retailer.id
        ).count(),
        'stocks': RetailerProduct.query.filter(
            RetailerProduct.retailer_id == retailer.id,
            RetailerProduct.sold_date.is_(None)
        ).count(),
        'sold': RetailerProduct.query.filter(
            RetailerProduct.retailer_id == retailer.id,
            RetailerProduct.sold_date.isnot(None),
            RetailerProduct.invoice_item_id.is_(None)
        ).count(),
        'invoices': Invoice.query.filter(
            Invoice.retailer_id == retailer.id
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
            form.populate_obj(retailer)
            retailer.fees_proportion = form.fees_proportion.data / 100
            if not retailer.id:
                db.session.add(retailer)
            db.session.commit()
            flash('Retailer updated.', 'success')
            kwargs = {
                'retailer_id': retailer.id,
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


@retailers_bp.route('/<int:retailer_id>/sold/')
@login_required
def sold(retailer_id):
    retailer = Retailer.query.get(retailer_id)
    context = {
        'retailer': retailer,
        'stocks': retailer.stocks.filter(
            RetailerProduct.sold_date.isnot(None),
            RetailerProduct.invoice_item_id.is_(None)
        ),
        'tab_counts': tab_counts(retailer),
    }
    return render_template('retailers/sold.html', **context)


@retailers_bp.route('/<int:retailer_id>/invoices/')
@login_required
def invoices(retailer_id):
    retailer = Retailer.query.get(retailer_id)
    context = {
        'retailer': retailer,
        'invoices': retailer.invoices,
        'tab_counts': tab_counts(retailer),
    }
    return render_template('retailers/invoices.html', **context)


@retailers_bp.route('/<int:retailer_id>/invoices/<int:invoice_id>/')
@login_required
def invoice(retailer_id, invoice_id):
    retailer = Retailer.query.get(retailer_id)
    invoice = Invoice.query.get(invoice_id)
    context = {
        'retailer': retailer,
        'invoice': invoice,
    }
    return render_template('retailers/invoice.html', **context)


@retailers_bp.route('/<int:retailer_id>/invoices/', methods=['POST'])
@login_required
def make_invoice(retailer_id):
    retailer = Retailer.query.get(retailer_id)
    retailer_product_ids = request.form.getlist('retailer_product_ids[]')
    if not retailer:
        return abort(404)
    invoice = Invoice()
    db.session.add(invoice)
    invoice.retailer_id = retailer.id
    for retailer_product_id in retailer_product_ids:
        retailer_product = RetailerProduct.query.get(retailer_product_id)
        excl_tax_unit_price = retailer_product.product.unit_price / g.config['APP_VAT']
        tax = retailer_product.product.unit_price - excl_tax_unit_price

        invoice_item = invoice.items.filter(
            InvoiceItem.orders.any(
                RetailerProduct.product_id == retailer_product.product_id)).first()
        if not invoice_item:
            invoice_item = InvoiceItem()
            invoice_item.title = retailer_product.product.title
            invoice_item.unit_price = excl_tax_unit_price
        invoice_item.orders.append(retailer_product)

        invoice_item.quantity = invoice_item.orders.count()
        invoice_item.excl_tax_price = excl_tax_unit_price * invoice_item.quantity
        invoice_item.tax_price = tax * invoice_item.quantity
        invoice_item.incl_tax_price = invoice_item.excl_tax_price + invoice_item.tax_price

        invoice.items.append(invoice_item)
    db.session.commit()
    if tabapp.utils.request_wants_json():
        return jsonify(success='Product pay.', tab_counts=tab_counts(retailer))
    flash('Product pay.', 'success')
    kwargs = {
        'retailer_id': retailer.id,
    }
    return redirect(url_for('retailers_bp.sold', **kwargs))
