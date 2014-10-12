# -*- coding: utf-8 -*-

from datetime import date
from flask import Blueprint, request, render_template,\
    redirect, url_for, flash, current_app, jsonify, abort
from flask.ext.login import login_required
from tabapp.models import db, Retailer, Product, RetailerProduct
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
            RetailerProduct.sold_date.isnot(None)
        ).count(),
        'invoices': RetailerProduct.query.filter(
            RetailerProduct.retailer_id == retailer.id,
            RetailerProduct.payment_date.isnot(None)
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
            for product_id, quantity in cart:
                if not quantity:
                    continue
                for i in range(quantity):
                    retailer_product = RetailerProduct()
                    retailer_product.retailer_id = retailer.id
                    retailer_product.product_id = product_id
                    retailer_product.order_date = date.today()
                    current_app.logger.debug(str(retailer_product))
                    retailer.stocks.append(retailer_product)
            current_app.logger.debug(str(retailer))
            db.session.commit()
            kwargs = {
                retailer_id: retailer_id,
            }
            return redirect(url_for('retailers_supplies_bp.index', **kwargs))
        except Exception as e:
            for msg in e.args:
                flash(msg, 'error')
    page = int(request.args.get('page', 1))
    products = Product.query.paginate(page)
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
        return jsonify(success='Product sold.')
    flash('Product sold.', 'success')
    kwargs = {
        retailer_id: retailer.id,
    }
    return redirect(url_for('retailers_supplies_bp.index', **kwargs))


@retailers_supplies_bp.route('/<int:retailer_id>/supplies/<int:retailer_product_id>/', methods=['DELETE'])
@login_required
def delete(retailer_id, retailer_product_id):
    retailer = Retailer.query.get(retailer_id)
    retailer_product = RetailerProduct.query.get(retailer_product_id)
    if not retailer or not retailer_product or retailer.id != retailer_product.retailer_id:
        return abort(404)
    db.session.delete(retailer_product)
    db.session.commit()
    if tabapp.utils.request_wants_json():
        return jsonify(success='Product deleted from stocks.')
    flash('Product deleted from stocks.', 'success')
    kwargs = {
        retailer_id: retailer.id,
    }
    return redirect(url_for('retailers_supplies_bp.index', **kwargs))
