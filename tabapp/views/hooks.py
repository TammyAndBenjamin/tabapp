# -*- coding: utf-8 -*-

from flask import Blueprint, request, g, current_app, abort, jsonify, make_response
from flask.ext.babel import gettext as _
from flask.ext.cors import cross_origin
from tabapp.extensions.security import csrf
from tabapp.models import db, Product, Lead, ProductOrder
import tabapp.utils
import decimal

hooks_bp = Blueprint('hooks_bp', __name__, subdomain='hooks')


@csrf.exempt
@tabapp.utils.shopify_webhook
@hooks_bp.route('/products/', methods=['POST'])
def products():
    if not g.config['SYNC_ACTIVE']:
        return ''
    topic = request.headers.get('X-Shopify-Topic')
    product_id = request.headers.get('X-Shopify-Product-Id')
    data = request.get_json()
    callbacks = {
        'products/create': ProductAction.add,
        'products/update': ProductAction.update,
        'products/delete': ProductAction.delete,
    }
    callbacks[topic](product_id, data)
    return 'ok'


@csrf.exempt
@tabapp.utils.shopify_webhook
@hooks_bp.route('/product_orders/', methods=['POST'])
def product_orders():
    if not g.config['SYNC_ACTIVE']:
        return ''
    topic = request.headers.get('X-Shopify-Topic')
    product_order_id = request.headers.get('X-Shopify-Order-Id')
    data = request.get_json()
    callbacks = {
        'orders/paid': ProductOrderAction.upsert,
        'orders/updated': ProductOrderAction.upsert,
        'orders/delete': ProductOrderAction.delete,
        'orders/cancelled': ProductOrderAction.delete,
    }
    callbacks[topic](product_order_id, data)
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


class ProductAction(object):
    @staticmethod
    def add(product_id, data):
        tags = data.get('tags', '').split(', ')
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


    @staticmethod
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


    @staticmethod
    def delete(product_id, data):
        product = Product.query.filter(Product.remote_id == data.get('id')).first()
        if not product:
            return True
        db.session.delete(product)
        db.session.commit()


class ProductOrderAction(object):
    @staticmethod
    def upsert(product_order_id, data):
        product_order = ProductOrder.query.filter(ProductOrder.remote_id == product_order_id).first()
        if not product_order:
            product_order = ProductOrder()
            product_order.remote_id = product_order_id
            shipping_address = data.get('shipping_address')
            product_order.name = data.get('name')
            product_order.shipping_country = shipping_address['country_code'] if shipping_address else 'FR'
            product_order.subtotal_price = decimal.Decimal(data.get('subtotal_price', '0'))
            product_order.total_tax = decimal.Decimal(data.get('total_tax', '0'))
            product_order.total_price = decimal.Decimal(data.get('total_price', '0'))
            product_order.financial_status = data.get('financial_status')
            db.session.add(product_order)
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
            return True
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
        current_app.logger.info('Product order {} upsert.'.format(product_order.id))


    @staticmethod
    def delete(product_order_id, data):
        product_order = ProductOrder.query.filter(ProductOrder.remote_id == product_order_id).first()
        if not product_order:
            return True
        db.session.delete(product_order)
        db.session.commit()
