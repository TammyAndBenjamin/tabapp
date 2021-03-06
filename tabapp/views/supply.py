# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, jsonify, make_response, abort
from tabapp.utils import list_from_resource, noindex
import decimal
import re

supply_bp = Blueprint('supply_bp', __name__, subdomain='data')

def get_products():
    def get_image_from_size(url, size):
        if size == 'original':
            return url
        pattern = r'(\.(jpg|jpeg)\?)'
        return re.sub(pattern, r'_{}\1'.format(size), url, flags=re.IGNORECASE)
    quantity_buffer = 1
    fields = [
        'id',
        'title',
        'product_type',
        'images',
        'body_html',
        'handle',
        'variants',
    ]
    resource = 'products'
    params = '?page={{page}}&fields={fields}&collection_id={collection_id}&published_status=published'.format(**{
        'fields': ','.join(fields),
        'collection_id': 15219609,  # Collection -> Tous les produits
    })
    rows = list_from_resource(resource, params)
    products = []
    product_url = 'http://www.tammyandbenjamin.com/products/{}'
    for row in rows:
        images_source = [ image.get('src') for image in row.get('images') ]
        sizes = ['original', 'large', 'medium', 'small']
        images = [{ size: get_image_from_size(image_source, size) for size in sizes }
            for image_source in images_source]
        variant = row.get('variants')[0]
        quantity_variant = int(variant.get('inventory_quantity'))
        remaining_amount = quantity_variant - quantity_buffer
        product = {
            'title': row.get('title'),
            'quantity': remaining_amount if remaining_amount > 0 else 0,
            'description': row.get('body_html'),
            'url': product_url.format(row.get('handle')),
            'price': decimal.Decimal(variant.get('price')),
            'sku': variant.get('sku'),
            'images': images,
            'category': row.get('product_type'),
            'gender': 'Female',
            'sizes': [],
            'colors': [],
            'sale_price': '',
        }
        products.append(product)
    return products

@supply_bp.route('/')
@noindex
def list():
    context = {
        'products': get_products(),
    }
    return render_template('supplies.html', **context)

@supply_bp.route('/<string:mediatype>')
@noindex
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
