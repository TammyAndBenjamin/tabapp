# -*- coding: utf-8 -*-

from datetime import datetime
from flask import Blueprint, request, g, current_app
from tabapp import csrf
from tabapp.models import db, Product

hooks_bp = Blueprint('hooks_bp', __name__, subdomain='hooks')


@csrf.exempt
@hooks_bp.route('/products/', methods=['POST'])
def products():
    h = request.headers.get('X-Shopify-Hmac-Sha256')
    topic = request.headers.get('X-Shopify-Topic')
    product_id = request.headers.get('X-Shopify-Product-Id')
    callbacks = {
        'products/create': add,
        'products/update': update,
        'products/delete': delete,
    }
    callbacks[topic](product_id, request.get_json())
    return 'ok'


def add(product_id, data):
    product = Product()
    product.remote_id = data.get('id')
    product.remote_variant_id = data.get('variants')[0].get('id')
    product.title = data.get('title')
    product.quantity = data.get('variants')[0].get('inventory_quantity')
    product.unit_price = data.get('variants')[0].get('price')
    if data.get('images'):
        product.image = data.get('images')[0].get('src')
    product.last_sync = datetime.now()
    db.session.add(product)
    db.session.commit()


def update(product_id, data):
    product = Product.query.filter(Product.remote_id == data.get('id')).first()
    if not product:
        return True
    product.title = data.get('title')
    product.quantity = data.get('variants')[0].get('inventory_quantity')
    product.unit_price = data.get('variants')[0].get('price')
    if data.get('images'):
        product.image = data.get('images')[0].get('src')
    product.last_sync = datetime.now()
    db.session.commit()


def delete(product_id, data):
    product = Product.query.filter(Product.remote_id == data.get('id')).first()
    if not product:
        return True
    db.session.delete(product)
    db.session.commit()
