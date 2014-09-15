# -*- coding: utf-8 -*-

from flask import Blueprint, request, render_template, jsonify, g
from utils import list_from_resource
import math
import psycopg2.extras

retailers_bp = Blueprint('retailers_bp', __name__, subdomain='backyard')


@retailers_bp.route('/')
def index():
    cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    page = int(request.args.get('page', 1))
    fields = [
        'id',
        'title',
        'images',
    ]
    resource = 'products'
    params = '?page={{page}}&fields={fields}&published_status=published'.format(**{
        'fields': ','.join(fields),
    })
    max_page = math.ceil(list_from_resource(resource, params, count = True) / 50)
    rows = list_from_resource(resource, params, page)
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
        'products': products,
    }
    return render_template('retailers/index.html', **context)
