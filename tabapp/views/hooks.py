# -*- coding: utf-8 -*-

from flask import Blueprint, request, g, current_app, abort, jsonify, make_response
from flask.ext.babel import gettext as _
from flask.ext.cors import cross_origin
from tabapp import csrf
from tabapp.models import db, Product, Lead, ProductOrder
import tabapp.utils
import hashlib
import base64
import hmac
import decimal

hooks_bp = Blueprint('hooks_bp', __name__, subdomain='hooks')


def is_valid(remote_h, data):
    local_h = hmac.new(g.config['SHOPIFY_SECRET'].encode(), data, hashlib.sha256)
    encoded_local_h = base64.b64encode(local_h.digest())
    return remote_h == encoded_local_h


@csrf.exempt
@hooks_bp.route('/products/', methods=['POST'])
def products():
    if not g.config['SYNC_ACTIVE']:
        return ''
    remote_h = request.headers.get('X-Shopify-Hmac-Sha256')
    if not remote_h:
        current_app.logger.warning('Hmac signature not found')
        return abort(404)
    topic = request.headers.get('X-Shopify-Topic')
    product_id = request.headers.get('X-Shopify-Product-Id')
    data = request.get_json()
    #if not is_valid(remote_h, data):
        #current_app.logger.warning('Invalid Hmac signature for the hooks')
        #return abort(404)
    callbacks = {
        'products/create': add,
        'products/update': update,
        'products/delete': delete,
    }
    callbacks[topic](product_id, data)
    return 'ok'


@csrf.exempt
@hooks_bp.route('/product_orders/', methods=['POST'])
def product_orders():
    if not g.config['SYNC_ACTIVE']:
        return ''
    remote_h = request.headers.get('X-Shopify-Hmac-Sha256')
    if not remote_h:
        current_app.logger.warning('Hmac signature not found')
        return abort(404)
    topic = request.headers.get('X-Shopify-Topic')
    product_order_id = request.headers.get('X-Shopify-Order-Id')
    data = request.get_json()
    #if not is_valid(remote_h, data):
        #current_app.logger.warning('Invalid Hmac signature for the hooks')
        #return abort(404)
    if not product_order_id:
        product_order_id = data.get('order_id')
    product_order = ProductOrder.query.filter(ProductOrder.remote_id == product_order_id).first()
    is_new = (product_order == None)
    if not product_order:
        product_order = ProductOrder()
        product_order.remote_id = product_order_id
        db.session.add(product_order)
    if is_new and topic == 'orders/paid':
        shipping_address = data.get('shipping_address')
        product_order.name = data.get('name')
        product_order.shipping_country = shipping_address['country_code'] if shipping_address else 'FR'
        product_order.subtotal_price = decimal.Decimal(data.get('subtotal_price', '0'))
        product_order.total_tax = decimal.Decimal(data.get('total_tax', '0'))
        product_order.total_price = decimal.Decimal(data.get('total_price', '0'))
        product_order.financial_status = data.get('financial_status')
    fields = [
        'id',
        'kind',
        'status',
        'amount',
        'created_at',
    ]
    resource = 'orders/{}/transactions'.format(product_order.remote_id)
    params = '?page={{page}}&limit={{limit}}&fields={fields}'.format(**{
        'fields': ','.join(fields),
    })
    transactions = tabapp.utils.list_from_resource(resource, params, key='transactions', page=1)
    if not transactions:
        return 'ok'
    transaction_ids = []
    paid_price = 0
    refunded_price = 0
    product_order.date = min([transaction.get('created_at') for transaction in transactions])
    for transaction in transactions:
        if not transaction.get('status') == 'success':
            continue
        if transaction.get('kind') in ['authorization', 'void']:
            continue
        transaction_ids.append(transaction.get('id'))
        if transaction.get('kind') in ['capture', 'sale']:
            paid_price += decimal.Decimal(transaction.get('amount'))
        if transaction.get('kind') in ['refund']:
            refunded_price += decimal.Decimal(transaction.get('amount'))
    product_order.transaction_ids = transaction_ids
    product_order.paid_price = paid_price
    product_order.refunded_price = refunded_price
    db.session.commit()
    return 'ok'


@csrf.exempt
@hooks_bp.route('/subscribe/', methods=['POST'])
@cross_origin(origins=['http://www.tammyandbenjamin.com', 'http://tabdev.myshopify.com/'])
def subscribe():
    try:
        token = request.form['b_1c3be4482a6a53fea9c9c2e39_423d8800d8']
        if token:
            raise ValueError()
    except (KeyError, ValueError):
        abort(404)
    lead_email = request.form['lead_email']
    lead = Lead()
    lead.email = lead_email
    db.session.add(lead)
    db.session.commit()
    content = jsonify(success=_('Your email was successfully registered'))
    response = make_response(content)
    response.headers['Access-Control-Allow-Origin'] = request.headers['Origin']
    return response


def add(product_id, data):
    tags = row.get('tags', '').split(', ')
    product = Product()
    product.remote_id = data.get('id')
    product.remote_variant_id = data.get('variants')[0].get('id')
    product.title = data.get('title')
    product.quantity = data.get('variants')[0].get('inventory_quantity')
    product.unit_price = data.get('variants')[0].get('price')
    if data.get('images'):
        product.image = data.get('images')[0].get('src')
    product.is_wholesale = 'WHOLESALE' in tags
    db.session.add(product)
    db.session.commit()
    current_app.logger.info('Product {} added.'.format(product.id))


def update(product_id, data):
    tags = row.get('tags', '').split(', ')
    product = Product.query.filter(Product.remote_id == data.get('id')).first()
    if not product:
        return True
    product.title = data.get('title')
    product.quantity = data.get('variants')[0].get('inventory_quantity')
    product.unit_price = data.get('variants')[0].get('price')
    if data.get('images'):
        product.image = data.get('images')[0].get('src')
    product.is_wholesale = 'WHOLESALE' in tags
    db.session.commit()
    current_app.logger.info('Product {} updated.'.format(product.id))


def delete(product_id, data):
    product = Product.query.filter(Product.remote_id == data.get('id')).first()
    if not product:
        return True
    db.session.delete(product)
    db.session.commit()
