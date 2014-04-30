# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, jsonify, make_response, abort
from utils import list_from_resource, process_orders
import requests
import json

supply_bp = Blueprint('supply_bp', __name__)

def get_products():
    quantity_buffer = 2
    fields = [
        'title',
        'variants',
    ]
    resource = 'products'
    params = '?page={{page}}&fields={fields}'.format(**{
        'fields': ','.join(fields),
    })
    rows = list_from_resource('products', params)
    products = []
    for row in rows:
        quantity_variant = int(row.get('variants')[0].get('inventory_quantity'))
        remaining_amount = quantity_variant - quantity_buffer
        product = {
            'title': row.get('title'),
            'quantity': remaining_amount if remaining_amount > 0 else 0,
        }
        products.append(product)
    return products

@supply_bp.route('/')
def list():
    context = {
        'products': get_products(),
    }
    return render_template('supplies.html', **context)

@supply_bp.route('/<string:mediatype>')
def raw(mediatype):
    context = {
        'products': get_products(),
    }
    response = None
    if mediatype == 'json':
        response = jsonify(**context)
    if mediatype == 'xml':
        response = make_response(render_template('supplies.xml', **context))
        response.mimetype = 'text/xml'
    if not response:
        abort(404)
    return response
