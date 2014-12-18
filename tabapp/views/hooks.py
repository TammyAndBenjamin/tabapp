# -*- coding: utf-8 -*-

from datetime import datetime
from flask import Blueprint, request, g, current_app, abort, jsonify, make_response
from flask.ext.babel import gettext as _
from flask.ext.cors import cross_origin
from tabapp import csrf
from tabapp.models import db, Product, Lead
import hashlib
import base64
import hmac

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
    content = jsonify(success=_('Vos coordonnées ont bien été prises en compte.'))
    response = make_response(content)
    response.headers['Access-Control-Allow-Origin'] = request.headers['Origin']
    return response


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
    current_app.logger.info('Product {} added.'.format(product.id))


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
    current_app.logger.info('Product {} updated.'.format(product.id))


def delete(product_id, data):
    product = Product.query.filter(Product.remote_id == data.get('id')).first()
    if not product:
        return True
    db.session.delete(product)
    db.session.commit()
