# -*- coding: utf-8 -*-

from datetime import date
from flask import Blueprint, request, render_template,\
    redirect, url_for, flash, current_app, jsonify, abort, g
from flask.ext.login import login_required
from tabapp.models import db, Invoice, Retailer, Product,\
    RetailerProduct, DeliverySlip, DeliverySlipLine
import tabapp.utils
import decimal
import math
import sqlalchemy
import sqlalchemy.dialects.postgresql


bp_name = 'retailers_supplies_bp'
retailers_supplies_bp = Blueprint(bp_name, __name__, subdomain='backyard')


def tab_counts(retailer):
    counts = {
        'supplies': RetailerProduct.query.filter(
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


@retailers_supplies_bp.route('/<int:retailer_id>/supplies/', methods=['GET'])
@login_required
def index(retailer_id):
    retailer = Retailer.query.get(retailer_id)
    context = {
        'retailer': retailer,
        'stocks': retailer.stocks.filter(RetailerProduct.sold_date.is_(None)),
        'tab_counts': tab_counts(retailer),
    }
    return render_template('retailers/supplies.html', **context)


@retailers_supplies_bp.route('/<int:retailer_id>/supplies/add', methods=['GET', 'POST'])
@login_required
def add(retailer_id):
    retailer = Retailer.query.get(retailer_id)
    if request.method == 'POST':
        try:
            product_ids = [int(v) for v in request.form.getlist('product_id')]
            quantities = [int(v) for v in request.form.getlist('quantity')]
            cart = zip(product_ids, quantities)
            delivery_slip = DeliverySlip()
            db.session.add(delivery_slip)
            delivery_slip.retailer_id = retailer.id
            for product_id, quantity in cart:
                if not quantity:
                    continue
                product = Product.query.get(product_id)
                delivery_slip_line = DeliverySlipLine()
                delivery_slip_line.product_id = product.id
                delivery_slip_line.fees = retailer.fees_proportion
                delivery_slip_line.quantity = delivery_slip_line.orders.count()
                for i in range(quantity):
                    retailer_product = RetailerProduct()
                    retailer_product.retailer_id = retailer.id
                    retailer_product.product_id = product_id
                    retailer_product.order_date = date.today()
                    retailer.stocks.append(retailer_product)
                    delivery_slip_line.orders.append(retailer_product)
                delivery_slip_line.quantity = quantity
                delivery_slip_line.recommanded_price = product.unit_price * delivery_slip_line.quantity
                delivery_slip_line.incl_tax_price = delivery_slip_line.recommanded_price * (1 - delivery_slip_line.fees)
                delivery_slip_line.excl_tax_price = delivery_slip_line.incl_tax_price / g.config['APP_VAT']
                delivery_slip_line.tax_price = delivery_slip_line.incl_tax_price - delivery_slip_line.excl_tax_price
                delivery_slip.lines.append(delivery_slip_line)
                product = Product.query.get(product_id)
                product.quantity = product.quantity - quantity
                remote_url = '{}variants/{{}}.json'.format(g.config['SHOPIFY_URL'])
                product.push_to_remote(remote_url, quantity * -1)
            db.session.commit()
            kwargs = {
                'retailer_id': retailer_id,
            }
            return redirect(url_for('retailers_supplies_bp.index', **kwargs))
        except Exception as e:
            db.session.rollback()
            for msg in e.args:
                flash(msg, 'error')
    page = int(request.args.get('page', 1))
    products = Product.query.filter(Product.quantity > 0).order_by(Product.title).paginate(page)
    context = {
        'retailer': retailer,
        'tab_counts': tab_counts(retailer),
        'products': products.items,
        'page': products.page,
        'max_page': products.pages,
    }
    return render_template('retailers/products.html', **context)


@retailers_supplies_bp.route('/<int:retailer_id>/supplies/<int:retailer_product_id>/sell', methods=['POST'])
@login_required
def sell(retailer_id, retailer_product_id):
    retailer = Retailer.query.get(retailer_id)
    retailer_product = RetailerProduct.query.get(retailer_product_id)
    if not retailer or not retailer_product or retailer.id != retailer_product.retailer_id:
        return abort(404)
    retailer_product.sold_date = date.today()
    db.session.commit()
    if tabapp.utils.request_wants_json():
        return jsonify(success='Product sold.', tab_counts=tab_counts(retailer))
    flash('Product sold.', 'success')
    kwargs = {
        'retailer_id': retailer.id,
    }
    return redirect(url_for('retailers_supplies_bp.index', **kwargs))


@retailers_supplies_bp.route('/<int:retailer_id>/supplies/<int:retailer_product_id>/', methods=['DELETE'])
@login_required
def delete(retailer_id, retailer_product_id):
    retailer = Retailer.query.get(retailer_id)
    retailer_product = RetailerProduct.query.get(retailer_product_id)
    if not retailer or not retailer_product or retailer.id != retailer_product.retailer_id:
        return abort(404)
    try:
        db.session.delete(retailer_product)
        product = Product.query.get(retailer_product.product_id)
        product.quantity = product.quantity + 1
        remote_url = '{}variants/{{}}.json'.format(g.config['SHOPIFY_URL'])
        product.push_to_remote(remote_url, 1)
        db.session.commit()
        if tabapp.utils.request_wants_json():
            return jsonify(success='Product deleted from stocks.', tab_counts=tab_counts(retailer))
        flash('Product deleted from stocks.', 'success')
    except Exception as e:
        db.session.rollback()
        for msg in e.args:
            flash(msg, 'error')
    kwargs = {
        'retailer_id': retailer.id,
    }
    return redirect(url_for('retailers_supplies_bp.index', **kwargs))
