# -*- coding: utf-8 -*-

from flask import Blueprint, request, render_template, jsonify
from utils import list_from_resource, process_orders
import requests
import json

supply_bp = Blueprint('supply_bp', __name__)

@supply_bp.route('/')
def index():
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
    context = {
        'products': products,
    }
    return render_template('supplies.html', **context)
