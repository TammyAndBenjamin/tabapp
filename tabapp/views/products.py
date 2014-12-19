# -*- coding: utf-8 -*-

from flask import Blueprint, request, render_template,\
    jsonify, g, current_app, redirect, url_for, abort
from flask.ext.login import login_required
from flask.ext.babel import format_date, format_currency
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
    products_retailers = {}
    for product in products.items:
        product_retailers = products_retailers.get(product.id, {})
        for stock in product.stocks:
            retailer_id = stock.retailer.id
            retailer_url = url_for('retailers_bp.retailer', retailer_id=retailer_id)
            retailer_link = '<a href="{}">{}</a>'.format(retailer_url, stock.retailer.name)
            product_retailers[retailer_id] = retailer_link
        products_retailers[product.id] = product_retailers
    context = {
        'products': products.items,
        'products_retailers': products_retailers,
        'page': products.page,
        'max_page': products.pages,
    }
    return render_template('products/list.html', **context)


@products_bp.route('/sync', methods=['POST'])
@login_required
def sync():
    Product.sync_from_remote()
    if tabapp.utils.request_wants_json():
        return jsonify(success='Products sync.')
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
    product = Product.query.get(product_id)
    if not product:
        return abort(404)
    costs = []
    for product_cost in product.costs:
        costs.append({
            'date': format_date(product_cost.start_date),
            'value': format_currency(product_cost.value, 'EUR'),
        })
    return jsonify(costs=costs)
