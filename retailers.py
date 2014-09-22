# -*- coding: utf-8 -*-

from flask import Blueprint, request, render_template, g, redirect, url_for, flash, current_app
from flask.ext.login import login_required
from utils import list_from_resource
import math
import psycopg2.extras

retailers_bp = Blueprint('retailers_bp', __name__, subdomain='backyard')


def submit(form):
    cur = g.db.cursor()
    retailer_id = form.get('retailer_id')
    if not retailer_id:
        raise Exception('Please choose a retailer')
    product_ids = [ int(v) for v in form.getlist('product_id') ]
    quantities = [ int(v) for v in form.getlist('quantity') ]
    sql = '''
        INSERT INTO retailer_product(retailer_id, product_id, order_date)
        VALUES (%s, %s, current_date)
    '''
    cart = zip(product_ids, quantities)
    for product_id, quantity in cart:
        if not quantity:
            continue
        for i in range(quantity):
            cur.execute(sql, (retailer_id, product_id))
    return redirect(url_for('retailers_bp.orders', **{'retailer_id': retailer_id}))


@retailers_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        try: return submit(request.form)
        except Exception as e:
            for msg in e.args:
                flash(msg, 'error')
    cur.execute('''
        SELECT id, name
        FROM retailer
    ''')
    retailers = cur.fetchall()
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
    max_page = math.ceil(list_from_resource(resource, params, count = True) / limit)
    rows = list_from_resource(resource, params, limit=limit, page=page)
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


@retailers_bp.route('/orders')
@login_required
def orders():
    cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    retailer_id = int(request.args.get('retailer_id'))
    cur.execute('''
        SELECT
            product_id,
            retailer.name as retailer_name,
            array_agg(retailer_product.id) as product_order_ids
        FROM retailer_product
        JOIN retailer ON retailer.id = retailer_product.retailer_id
        WHERE retailer_id = %s
        AND sale_date IS NULL
        GROUP BY 1, 2
    ''', (retailer_id,))
    rows = cur.fetchall()
    product_orders = []
    products = []
    for row in rows:
        product_id = row['product_id']
        retailer_name = row['retailer_name']
        product_order_ids = row['product_order_ids']
        fields = [
            'id',
            'title',
            'images',
        ]
        resource = 'products/{}'.format(product_id)
        params = '?fields={fields}'.format(**{
            'fields': ','.join(fields),
        })
        product = list_from_resource(resource, params, key='product', page=1)
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
            product_orders.append(product_order)
    cur.execute('''
        SELECT id, name
        FROM retailer
    ''')
    retailers = cur.fetchall()
    context = {
        'retailer_id': retailer_id,
        'product_orders': product_orders,
        'retailers': retailers,
    }
    return render_template('retailers/orders.html', **context)
