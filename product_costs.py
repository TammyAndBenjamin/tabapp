# -*- coding: utf-8 -*-

from flask import Blueprint, request, render_template, jsonify, g
from utils import list_from_api, process_orders
import math

product_costs_bp = Blueprint('product_costs_bp', __name__)

@product_costs_bp.route('/')
def products_list():
    page = int(request.args.get('page', 1))
    cur = g.db.cursor()
    fields = [
        'id',
        'title',
        'variants',
    ]
    url = '{base_url}products.json?page={{page}}&fields={fields}'.format(**{
            'base_url': g.config['SHOPIFY_URL'],
            'fields': ','.join(fields),
        })
    max_page = math.ceil(len(list_from_api(url, 'products')) / 50)
    rows = list_from_api(url, 'products', page)
    products = []
    for row in rows:
        cur.execute('''
            SELECT value
            FROM product_cost
            WHERE product_id = %s
            AND daterange(start_date, end_date) @> current_date
            ORDER BY end_date DESC NULLS FIRST
        ''', (row.get('id'),))
        product_cost = cur.fetchone()
        product = {
            'id': row.get('id'),
            'title': row.get('title'),
            'price': row.get('variants')[0].get('price'),
            'cost': product_cost[0] if product_cost else None,
        }
        products.append(product)
    context = {
        'page': page,
        'max_page': max_page,
        'products': products,
    }
    return render_template('products.html', **context)

@product_costs_bp.route('/<int:product_id>', methods=['GET'])
def costs_history(product_id):
    cur = g.db.cursor()
    cur.execute('''
        SELECT value, start_date
        FROM product_cost
        WHERE product_id = %s
        AND daterange(start_date, end_date) @> current_date
        ORDER BY start_date ASC, end_date ASC NULLS LAST
    ''', (product_id,))
    rows = cur.fetchall()
    product_costs = []
    for row in rows:
        product_cost = {
            'date': row[1].isoformat(),
            'value': row[0],
        }
        product_costs.append(product_cost)
    return jsonify(costs=product_costs)

@product_costs_bp.route('/<int:product_id>', methods=['POST'])
def add_cost(product_id):
    pass
