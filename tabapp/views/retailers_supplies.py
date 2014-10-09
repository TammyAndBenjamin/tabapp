# -*- coding: utf-8 -*-

from datetime import date
from flask import Blueprint, request, render_template,\
    redirect, url_for, flash, current_app, jsonify, abort
from flask.ext.login import login_required
from tabapp.models import db, Retailer, RetailerProduct
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


def structure_from_rows(rows):
    for row in rows:
        product_id = row.product_id
        product_order_ids = row.product_order_ids
        product_order_dates = row.product_order_dates
        fields = [
            'id',
            'title',
            'variants',
            'images',
        ]
        resource = 'products/{}'.format(product_id)
        params = '?fields={fields}'.format(**{
            'fields': ','.join(fields),
        })
        _product = tabapp.utils.list_from_resource(resource, params, key='product', page=1)
        price_incl_tax = decimal.Decimal(_product.get('variants')[0].get('price'))
        price_excl_tax = decimal.Decimal(price_incl_tax / decimal.Decimal(1.2))
        fees_incl_tax = price_incl_tax * row.fees_proportion
        fees_excl_tax = price_excl_tax * row.fees_proportion
        product = {
            'id': _product.get('id'),
            'title': _product.get('title'),
            'retailer_price_excl_tax': price_excl_tax - fees_excl_tax,
            'retailer_price_incl_tax': price_incl_tax - fees_incl_tax,
            'tab_price_excl_tax': price_excl_tax,
            'tab_price_incl_tax': price_incl_tax,
            'orders': [],
        }
        product_orders = zip(product_order_ids, product_order_dates)
        for product_order_id, product_order_date in product_orders:
            product['orders'].append({
                'id': product_order_id,
                'order_date': product_order_date,
            })
        yield product


@retailers_supplies_bp.route('/<int:retailer_id>/supplies/', methods=['GET'])
@login_required
def index(retailer_id):
    retailer = Retailer.query.get(retailer_id)
    retailer_products = db.session.query(
        RetailerProduct.product_id,
        Retailer.fees_proportion,
        sqlalchemy.func.array_agg(
            RetailerProduct.id,
            type_=sqlalchemy.dialects.postgresql.ARRAY(db.Integer)
        ).label('product_order_ids'),
        sqlalchemy.func.array_agg(
            RetailerProduct.order_date,
            type_=sqlalchemy.dialects.postgresql.ARRAY(db.Date)
        ).label('product_order_dates')
    ).join(Retailer).filter(
        RetailerProduct.retailer_id == retailer.id,
        RetailerProduct.sold_date.is_(None)
    ).group_by(
        RetailerProduct.product_id,
        Retailer.fees_proportion
    )
    current_app.logger.debug(str(retailer_products))
    products = structure_from_rows(retailer_products)
    context = {
        'retailer': retailer,
        'products': products,
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
    fields = [
        'id',
        'title',
        'images',
        'variants',
    ]
    resource = 'products'
    limit = 50
    params = '?page={{page}}&limit={{limit}}&fields={fields}&published_status=published'.format(**{
        'fields': ','.join(fields),
    })
    max_page = math.ceil(tabapp.utils.list_from_resource(resource, params, count=True) / limit)
    rows = tabapp.utils.list_from_resource(resource, params, limit=limit, page=page)
    products = []
    for row in rows:
        if not row.get('variants')[0].get('inventory_quantity'):
            continue
        product = {
            'id': row.get('id'),
            'title': row.get('title'),
            'image': row.get('images')[0].get('src'),
            'max': row.get('variants')[0].get('inventory_quantity'),
        }
        products.append(product)
    context = {
        'tab_counts': tab_counts(retailer),
        'page': page,
        'max_page': max_page,
        'retailer': retailer,
        'products': products,
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
