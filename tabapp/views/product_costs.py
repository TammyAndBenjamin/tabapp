# -*- coding: utf-8 -*-

from flask import Blueprint, request, render_template, jsonify, g, current_app
from flask.ext.login import login_required
from tabapp import db
from tabapp.models import ProductCost
from datetime import date
import tabapp.utils
import math
import sqlalchemy
import sqlalchemy.sql.expression
import sqlalchemy.dialects.postgresql


product_costs_bp = Blueprint('product_costs_bp', __name__, subdomain='backyard')


def current_cost(product_id, cost_date = None):
    if not cost_date:
        cost_date = date.today()
    product_cost = db.session.query(
        ProductCost.id,
        ProductCost.value
    ).filter(
        ProductCost.product_id==int(product_id),
        sqlalchemy.sql.expression.cast(sqlalchemy.func.daterange(
            ProductCost.start_date,
            ProductCost.end_date
        ), sqlalchemy.dialects.postgresql.DATERANGE).contains(cost_date)
    ).order_by(
        sqlalchemy.desc(ProductCost.end_date).nullsfirst(),
    ).first()
    return product_cost


@product_costs_bp.route('/')
@login_required
def index():
    page = int(request.args.get('page', 1))
    fields = [
        'id',
        'title',
        'variants',
    ]
    resource = 'products'
    params = '?page={{page}}&fields={fields}&published_status=published'.format(**{
        'fields': ','.join(fields),
    })
    max_page = math.ceil(tabapp.utils.list_from_resource(resource, params, count = True) / 50)
    rows = tabapp.utils.list_from_resource(resource, params, page)
    products = []
    for row in rows:
        product_cost = current_cost(row.get('id'))
        product = {
            'id': row.get('id'),
            'title': row.get('title'),
            'price': row.get('variants')[0].get('price'),
            'cost': product_cost.value if product_cost else None,
        }
        products.append(product)
    context = {
        'page': page,
        'max_page': max_page,
        'products': products,
    }
    return render_template('costs.html', **context)


@product_costs_bp.route('/<int:product_id>', methods=['GET'])
@login_required
def costs_history(product_id):
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


@product_costs_bp.route('/<int:product_id>', methods=['POST'])
@login_required
def add_cost(product_id):
    product_cost = current_cost(product_id)
    if product_cost:
        product_cost.end_date = date.today()
    product_cost = ProductCost()
    product_cost.product_id = product_id
    product_cost.value = request.form.get('product_cost')
    product_cost.start_date = date.today()
    db.session.add(product_cost)
    db.session.commit()
    return jsonify(result=True)
