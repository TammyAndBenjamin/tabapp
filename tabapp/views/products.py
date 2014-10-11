# -*- coding: utf-8 -*-

from flask import Blueprint, request, render_template, jsonify, g, current_app, redirect, url_for
from flask.ext.login import login_required
from tabapp.models import db, Product, ProductCost
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
    page = int(request.args.get('page', 1))
    products = Product.query.paginate(page)
    context = {
        'products': products.items,
        'page': products.page,
        'max_page': products.pages,
    }
    return render_template('products/list.html', **context)


@products_bp.route('/sync', methods=['POST'])
@login_required
def sync():
    Product.sync_from_remote()
    return redirect(url_for('products_bp.index'))


@products_bp.route('/<int:product_id>/costs', methods=['GET', 'POST'])
@login_required
def costs(product_id):
    if request.method == 'POST':
        product_cost = tabapp.utils.current_product_cost(product_id)
        if product_cost:
            product_cost.end_date = date.today()
        product_cost = ProductCost()
        product_cost.product_id = product_id
        product_cost.value = request.form.get('product_cost')
        product_cost.start_date = date.today()
        db.session.add(product_cost)
        db.session.commit()
        return jsonify(result=True)
    rows = db.session.query(
        ProductCost.id,
        ProductCost.value,
        ProductCost.start_date
    ).filter(
        ProductCost.product_id==int(product_id),
        sqlalchemy.sql.expression.cast(sqlalchemy.func.daterange(
            ProductCost.start_date,
            ProductCost.end_date
        ), sqlalchemy.dialects.postgresql.DATERANGE).contains(date.today())
    ).order_by(
        sqlalchemy.desc(ProductCost.end_date).nullsfirst(),
        sqlalchemy.desc(ProductCost.start_date)
    )
    product_costs = []
    for row in rows:
        product_cost = {
            'date': row.start_date.isoformat(),
            'value': row.value,
        }
        product_costs.append(product_cost)
    return jsonify(costs=product_costs)
