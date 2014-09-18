# -*- coding: utf-8 -*-

from flask import Blueprint, request, render_template, g, redirect, url_for, flash
from utils import list_from_resource
import math
import psycopg2.extras

retailers_bp = Blueprint('retailers_bp', __name__, subdomain='backyard')


@retailers_bp.route('/', methods=['GET'])
def index():
    cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
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
    limit = 20
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


@retailers_bp.route('/', methods=['POST'])
def submit():
    cur = g.db.cursor()
    retailer_id = request.form.get('retailer_id')
    if not retailer_id:
        flash('Please choose a retailer', 'error')
        return redirect(url_for('retailers_bp.index'))
    product_ids = [ int(v) for v in request.form.getlist('product_id') ]
    quantities = [ int(v) for v in request.form.getlist('quantity') ]
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
    return redirect(url_for('retailers_bp.orders'))


@retailers_bp.route('/orders')
def orders():
    return 'done'
