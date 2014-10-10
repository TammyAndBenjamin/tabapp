# -*- coding: utf-8 -*-

from flask import Blueprint, request, render_template, jsonify, g, current_app, redirect, url_for
from flask.ext.login import login_required
from tabapp.models import db, Product
from datetime import datetime, date
import tabapp.utils
import math
import sqlalchemy
import sqlalchemy.sql.expression
import sqlalchemy.dialects.postgresql


products_bp = Blueprint('products_bp', __name__, subdomain='backyard')


@products_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1)
    products = Product.query.paginate(page)
    context = {
        'products': products.items,
        'page': products.page,
        'max_page': products.pages,
    }
    return render_template('products/list.html', **context)


@products_bp.route('/sync')
@login_required
def sync():
    fields = [
        'id',
        'title',
        'updated_at',
        'images',
        'variants',
    ]
    resource = 'products'
    params = '?page={{page}}&fields={fields}&published_status=published'.format(**{
        'fields': ','.join(fields),
    })
    rows = tabapp.utils.list_from_resource(resource, params)
    for row in rows:
        product = Product.query.filter(Product.remote_id == row.get('id')).first()
        if product and product.last_sync.isoformat() >= row.get('updated_at'):
            continue
        if not product:
            product = Product()
            product.remote_id = row.get('id')
        product.title = row.get('title')
        product.quantity = row.get('variants')[0].get('inventory_quantity')
        product.unit_price = row.get('variants')[0].get('price')
        product.image = row.get('images')[0].get('src')
        product.last_sync = datetime.now()
        if not product.id:
            db.session.add(product)
    db.session.commit()
    return redirect(url_for('products_bp.index'))
