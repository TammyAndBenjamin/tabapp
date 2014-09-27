# -*- coding: utf-8 -*-

from datetime import date
from flask import Blueprint, request, render_template, g, redirect, url_for, flash, current_app
from flask.ext.login import login_required
from tabapp import db
from tabapp.models import Retailer, RetailerProduct
import tabapp.utils
import math
import sqlalchemy
import sqlalchemy.dialects.postgresql

retailers_bp = Blueprint('retailers_bp', __name__, subdomain='backyard')


def structure_from_rows(rows):
    for row in rows:
        product_id = row.product_id
        retailer_name = row.name
        product_order_ids = row.product_order_ids
        fields = [
            'id',
            'title',
            'images',
        ]
        resource = 'products/{}'.format(product_id)
        params = '?fields={fields}'.format(**{
            'fields': ','.join(fields),
        })
        product = tabapp.utils.list_from_resource(resource, params, key='product', page=1)
        for product_order_id in product_order_ids:
            product_order = {
                'id': product_order_id,
                'retailer_name': retailer_name,
                'product': {
                    'id': product.get('id'),
                    'title': product.get('title'),
                    'image': product.get('images')[0].get('src'),
                }
            }
            yield product_order


def add_product_order(form):
    retailer_id = form.get('retailer_id')
    if not retailer_id:
        raise Exception('Please choose a retailer')
    product_ids = [ int(v) for v in form.getlist('product_id') ]
    quantities = [ int(v) for v in form.getlist('quantity') ]
    cart = zip(product_ids, quantities)
    for product_id, quantity in cart:
        if not quantity:
            continue
        for i in range(quantity):
            retailer_product = RetailerProduct()
            retailer_product.retailer_id = retailer_id
            retailer_product.product_id = product_id
            retailer_product.order_date = date.today()
            db.session.add(retailer_product)
    db.session.commit()
    return redirect(url_for('retailers_bp.invoices', **{'retailer_id': retailer_id}))


def sold_product_order(form):
    retailer_id = form.get('retailer_id')
    if not retailer_id:
        raise Exception('Please choose a retailer')
    product_order_ids = form.getlist('product_order_id')
    for product_order_id in product_order_ids:
        retailer_product = RetailerProduct.query.get(product_order_id)
        retailer_product.sold_date = date.today()
    db.session.commit()
    return redirect(url_for('retailers_bp.invoices', **{'retailer_id': retailer_id}))


def pay_product_order(form):
    retailer_id = form.get('retailer_id')
    if not retailer_id:
        raise Exception('Please choose a retailer')
    product_order_ids = form.getlist('product_order_id')
    for product_order_id in product_order_ids:
        retailer_product = RetailerProduct.query.get(product_order_id)
        retailer_product.payment_date = date.today()
    db.session.commit()
    return redirect(url_for('retailers_bp.invoices', **{'retailer_id': retailer_id}))


@retailers_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        try: return add_product_order(request.form)
        except Exception as e:
            for msg in e.args:
                flash(msg, 'error')
    retailers = Retailer.query.all()
    page = int(request.args.get('page', 1))
    fields = [
        'id',
        'title',
        'images',
    ]
    resource = 'products'
    limit = 50
    params = '?page={{page}}&limit={{limit}}&fields={fields}&published_status=published'.format(**{
        'fields': ','.join(fields),
    })
    max_page = math.ceil(tabapp.utils.list_from_resource(resource, params, count = True) / limit)
    rows = tabapp.utils.list_from_resource(resource, params, limit=limit, page=page)
    products = []
    for row in rows:
        product = {
            'id': row.get('id'),
            'title': row.get('title'),
            'image': row.get('images')[0].get('src'),
        }
        products.append(product)
    context = {
        'page': page,
        'max_page': max_page,
        'retailers': retailers,
        'products': products,
    }
    return render_template('retailers/index.html', **context)


@retailers_bp.route('/orders', methods=['GET', 'POST'])
@login_required
def orders():
    if request.method == 'POST':
        try: return sold_product_order(request.form)
        except Exception as e:
            for msg in e.args:
                flash(msg, 'error')
    retailer_id = int(request.args.get('retailer_id'))
    retailer_products = db.session.query(
        RetailerProduct.product_id,
        Retailer.name,
        sqlalchemy.func.array_agg(
            RetailerProduct.id,
            type_=sqlalchemy.dialects.postgresql.ARRAY(db.Integer)
        ).label('product_order_ids')
    ).filter(RetailerProduct.sold_date==None).join(Retailer).group_by(
        RetailerProduct.product_id,
        Retailer.name
    )
    current_app.logger.debug(str(retailer_products))
    product_orders = structure_from_rows(retailer_products)
    retailers = Retailer.query.all()
    context = {
        'retailer_id': retailer_id,
        'product_orders': product_orders,
        'retailers': retailers,
    }
    return render_template('retailers/orders.html', **context)


@retailers_bp.route('/invoices', methods=['GET', 'POST'])
@login_required
def invoices():
    if request.method == 'POST':
        pass
        try: return pay_product_order(request.form)
        except Exception as e:
            for msg in e.args:
                flash(msg, 'error')
    retailer_id = int(request.args.get('retailer_id'))
    retailer_products = db.session.query(
        RetailerProduct.product_id,
        Retailer.name,
        sqlalchemy.func.array_agg(
            RetailerProduct.id,
            type_=sqlalchemy.dialects.postgresql.ARRAY(db.Integer)
        ).label('product_order_ids')
    ).filter(RetailerProduct.payment_date==None).join(Retailer).group_by(
        RetailerProduct.product_id,
        Retailer.name
    )
    product_orders = structure_from_rows(retailer_products)
    retailers = Retailer.query.all()
    context = {
        'retailer_id': retailer_id,
        'product_orders': product_orders,
        'retailers': retailers,
    }
    return render_template('retailers/invoices.html', **context)
