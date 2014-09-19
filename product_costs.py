# -*- coding: utf-8 -*-

from flask import Blueprint, request, render_template, jsonify, g
from flask.ext.login import login_required
from utils import list_from_resource
import math
import psycopg2.extras

product_costs_bp = Blueprint('product_costs_bp', __name__, subdomain='backyard')

def current_cost(cur, product_id):
    cur.execute('''
        SELECT id, value
        FROM product_cost
        WHERE product_id = %s
        AND daterange(start_date, end_date) @> current_date
        ORDER BY end_date DESC NULLS FIRST
    ''', (product_id,))
    product_cost = cur.fetchone()
    return product_cost

@product_costs_bp.route('/')
@login_required
def index():
    cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
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
    max_page = math.ceil(list_from_resource(resource, params, count = True) / 50)
    rows = list_from_resource(resource, params, page)
    products = []
    for row in rows:
        product_cost = current_cost(cur, row.get('id'))
        product = {
            'id': row.get('id'),
            'title': row.get('title'),
            'price': row.get('variants')[0].get('price'),
            'cost': product_cost['value'] if product_cost else None,
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
    cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('''
        SELECT value, start_date
        FROM product_cost
        WHERE product_id = %s
        ORDER BY end_date DESC NULLS FIRST, start_date DESC
    ''', (product_id,))
    rows = cur.fetchall()
    product_costs = []
    for row in rows:
        product_cost = {
            'date': row['start_date'].isoformat(),
            'value': row['value'],
        }
        product_costs.append(product_cost)
    return jsonify(costs=product_costs)

@product_costs_bp.route('/<int:product_id>', methods=['POST'])
@login_required
def add_cost(product_id):
    cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    product_cost = current_cost(cur, product_id)
    if product_cost:
        cur.execute('''
            UPDATE product_cost SET end_date = current_date WHERE id = %s
        ''', (product_cost['id'],))
    cur.execute('''
        INSERT INTO product_cost(product_id, value, start_date) VALUES(%s, %s, current_date)
    ''', (product_id, request.form.get('product_cost'),))
    return jsonify(result=True)
