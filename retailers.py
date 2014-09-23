# -*- coding: utf-8 -*-

from flask import Blueprint, request, render_template, g, redirect, url_for, flash, current_app
from flask.ext.login import login_required
import utils
import math
import psycopg2.extras

retailers_bp = Blueprint('retailers_bp', __name__, subdomain='backyard')


def structure_from_rows(rows):
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
        product = utils.list_from_resource(resource, params, key='product', page=1)
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
    sql = '''
        INSERT INTO retailer_product(retailer_id, product_id, order_date)
        VALUES (%s, %s, current_date)
    '''
    cart = zip(product_ids, quantities)
    for product_id, quantity in cart:
        if not quantity:
            continue
        for i in range(quantity):
            utils.execute(cur, sql, (retailer_id, product_id))
    return redirect(url_for('retailers_bp.invoices', **{'retailer_id': retailer_id}))


def sold_product_order(form):
    retailer_id = form.get('retailer_id')
    if not retailer_id:
        raise Exception('Please choose a retailer')
    product_order_ids = form.getlist('product_order_id')
    sql = '''
        UPDATE retailer_product
        SET sold_date = current_date
        WHERE id = %s
    '''
    for product_order_id in product_order_ids:
        utils.execute(cur, sql, (product_order_id,))
    return redirect(url_for('retailers_bp.invoices', **{'retailer_id': retailer_id}))


def pay_product_order(form):
    retailer_id = form.get('retailer_id')
    if not retailer_id:
        raise Exception('Please choose a retailer')
    product_order_ids = form.getlist('product_order_id')
    sql = '''
        UPDATE retailer_product
        SET payment_date = current_date
        WHERE id = %s
    '''
    for product_order_id in product_order_ids:
        utils.execute(cur, sql, (product_order_id,))
    return redirect(url_for('retailers_bp.orders', **{'retailer_id': retailer_id}))


@retailers_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        try: return add_product_order(request.form)
        except Exception as e:
            for msg in e.args:
                flash(msg, 'error')
    retailers = g.db.Retailer.all()
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
    max_page = math.ceil(utils.list_from_resource(resource, params, count = True) / limit)
    rows = utils.list_from_resource(resource, params, limit=limit, page=page)
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
    utils.execute(cur, '''
        SELECT
            product_id,
            retailer.name as retailer_name,
            array_agg(retailer_product.id) as product_order_ids
        FROM retailer_product
        JOIN retailer ON retailer.id = retailer_product.retailer_id
        WHERE retailer_id = %s
        AND sold_date IS NULL
        GROUP BY 1, 2
    ''', (retailer_id,))
    rows = cur.fetchall()
    product_orders = structure_from_rows(rows)
    utils.execute(cur, '''
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


@retailers_bp.route('/invoices', methods=['GET', 'POST'])
@login_required
def invoices():
    if request.method == 'POST':
        pass
        #try: return sold_product_order(request.form)
        #except Exception as e:
            #for msg in e.args:
                #flash(msg, 'error')
    retailer_id = int(request.args.get('retailer_id'))
    utils.execute(cur, '''
        SELECT
            product_id,
            retailer.name as retailer_name,
            array_agg(retailer_product.id) as product_order_ids
        FROM retailer_product
        JOIN retailer ON retailer.id = retailer_product.retailer_id
        WHERE retailer_id = %s
        AND sold_date IS NOT NULL
        AND payment_date IS NULL
        GROUP BY 1, 2
    ''', (retailer_id,))
    rows = cur.fetchall()
    product_orders = structure_from_rows(rows)
    utils.execute(cur, '''
        SELECT id, name
        FROM retailer
    ''')
    retailers = cur.fetchall()
    context = {
        'retailer_id': retailer_id,
        'product_orders': product_orders,
        'retailers': retailers,
    }
    return render_template('retailers/invoices.html', **context)
