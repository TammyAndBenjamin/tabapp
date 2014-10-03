# -*- coding: utf-8 -*-

from datetime import date
from flask import Blueprint, request, render_template, g, redirect, url_for, flash, current_app, jsonify
from flask.ext.login import login_required
from tabapp.models import db, Retailer, RetailerProduct
from tabapp.forms import RetailerForm
import tabapp.utils
import decimal
import math
import sqlalchemy
import sqlalchemy.dialects.postgresql

retailers_bp = Blueprint('retailers_bp', __name__, subdomain='backyard')


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


def tab_counts(retailer):
    counts = {
        'supplies': RetailerProduct.query.filter(
                RetailerProduct.retailer_id==retailer.id,
                RetailerProduct.sold_date==None
            ).count(),
        'sold': RetailerProduct.query.filter(
                RetailerProduct.retailer_id==retailer.id,
                RetailerProduct.sold_date!=None
            ).count(),
        'invoices': RetailerProduct.query.filter(
                RetailerProduct.retailer_id==retailer.id,
                RetailerProduct.payment_date!=None
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


@retailers_bp.route('/<int:retailer_id>', methods=['GET'])
@login_required
def retailer(retailer_id):
    retailer = Retailer.query.get(retailer_id)
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
@retailers_bp.route('/<int:retailer_id>', methods=['POST'])
@retailers_bp.route('/<int:retailer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_retailer(retailer_id):
    form = None
    if request.method == 'POST':
        form = RetailerForm(request.form)
        if form.validate():
            retailer = Retailer.query.get(retailer_id) if retailer_id else Retailer()
            retailer.name = form.name.data
            retailer.fees_proportion = form.fees_proportion.data / 100
            retailer.address = form.address.data
            if not retailer.id:
                db.session.add(retailer)
            db.session.commit()
            flash('Retailer updated.', 'success')
            return redirect(url_for('retailers_bp.retailer', retailer_id=retailer.id))
    retailer = Retailer.query.get(retailer_id) if retailer_id else Retailer()
    form = RetailerForm(obj=retailer) if not form else form
    form.fees_proportion.data = form.fees_proportion.data * 100 if form.fees_proportion.data else 0
    context = {
        'retailer_id': retailer.id,
        'form': form,
    }
    return render_template('retailers/form.html', **context)


@retailers_bp.route('/<int:retailer_id>', methods=['DELETE'])
@retailers_bp.route('/<int:retailer_id>/delete', methods=['POST'])
@login_required
def delete_retailer(retailer_id):
    retailer = Retailer.query.get(retailer_id)
    db.session.delete(retailer)
    db.session.commit()
    if tabapp.utils.request_wants_json():
        return jsonify(success='Retailer deleted.')
    flash('Retailer deleted.', 'success')
    return redirect(url_for('retailers_bp.index'))


@retailers_bp.route('/<int:retailer_id>/supplies', methods=['GET'])
@login_required
def supplies(retailer_id):
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
        RetailerProduct.retailer_id==retailer.id,
        RetailerProduct.sold_date==None
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


@retailers_bp.route('/<int:retailer_id>/supplies/add', methods=['GET', 'POST'])
@login_required
def add_supplies(retailer_id):
    retailer = Retailer.query.get(retailer_id)
    if request.method == 'POST':
        try:
            product_ids = [ int(v) for v in request.form.getlist('product_id') ]
            quantities = [ int(v) for v in request.form.getlist('quantity') ]
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
            return redirect(url_for('retailers_bp.supplies', **{'retailer_id': retailer_id}))
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
    max_page = math.ceil(tabapp.utils.list_from_resource(resource, params, count = True) / limit)
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


@retailers_bp.route('/<int:retailer_id>/sold', methods=['GET'])
@login_required
def sold(retailer_id):
    retailer = Retailer.query.get(retailer_id)
    context = {
        'retailer': retailer,
    }
    return render_template('retailers/sold.html', **context)


@retailers_bp.route('/<int:retailer_id>/invoices', methods=['GET'])
@login_required
def invoices(retailer_id):
    retailer = Retailer.query.get(retailer_id)
    context = {
        'retailer': retailer,
    }
    return render_template('retailers/invoices.html', **context)


@retailers_bp.route('/orders', methods=['GET', 'POST'])
@login_required
def orders():
    if request.method == 'POST':
        try: return sold_product_order(request.form)
        except Exception as e:
            for msg in e.args:
                flash(msg, 'error')
    retailer_id = int(request.args.get('retailer_id'))
    retailers = Retailer.query.all()
    context = {
        'retailer_id': retailer_id,
        'product_orders': product_orders,
        'retailers': retailers,
    }
    return render_template('retailers/orders.html', **context)
