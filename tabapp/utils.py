# -*- coding: utf-8 -*-

from functools import wraps
from flask import g, make_response, current_app, request, abort
from datetime import date
from tabapp.models import db, ProductCost
import decimal
import requests
import sqlalchemy
import sqlalchemy.sql.expression
import sqlalchemy.dialects.postgresql
import hashlib, base64, hmac, json


def add_response_headers(headers={}):
    """This decorator adds the headers passed in to the response"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            resp = make_response(f(*args, **kwargs))
            h = resp.headers
            for header, value in headers.items():
                h[header] = value
            return resp
        return decorated_function
    return decorator


def noindex(f):
    """This decorator passes X-Robots-Tag: noindex"""
    return add_response_headers({'X-Robots-Tag': 'noindex'})(f)


def shopify_webhook(f):
    """
      A decorator thats checks and validates a Shopify Webhook request.
    """
    def _hmac_is_valid(data, secret, hmac_to_verify):
        hash = hmac.new(secret, msg=data, digestmod=hashlib.sha256)
        hmac_calculated = base64.b64encode(hash.digest())
        return hmac.compare_digest(hmac_calculated, hmac_to_verify)

    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            request.headers['X-Shopify-Topic']
            webhook_hmac = request.headers['X-Shopify-Hmac-Sha256'].encode()
            json.loads(request.get_data().decode())
        except Exception as e:
            current_app.logger.error(e)
            return abort(400)
        if not _hmac_is_valid(request.get_data(), current_app.config['SHOPIFY_SECRET'].encode(), webhook_hmac):
            current_app.logger.error('HMAC not valid for webhook')
            return abort(403)
        return f(*args, **kwargs)
    return wrapper


def list_from_resource(resource, params, limit=None, page=None, count=False, key=None, _url=None):
    def make_requests(url, page, limit):
        url = url.format(**{'page': page, 'limit': limit})
        current_app.logger.debug(url)
        r = requests.get(url)
        return r.json()
    if not limit:
        limit = 50
    if not key:
        key = resource
    if not _url:
        _url = g.config['SHOPIFY_URL']
    url = '{}{}.json{}'.format(_url, resource, params)
    if count:
        url = url.replace(resource, '{}/count'.format(resource))
        data = make_requests(url, 1, limit)
        return int(data.get('count'))
    if page:
        data = make_requests(url, page, limit)
        rows = data.get(key)
    else:
        page = 1
        rows = []
        while True:
            data = make_requests(url, page, limit)
            result = data.get(key)
            if not result:
                break
            rows += result
            page += 1
    return rows


def current_product_cost(product_id, cost_date = None):
    if not cost_date:
        cost_date = date.today()
    product_cost = db.session.query(
        ProductCost.id,
        ProductCost.value
    ).filter(
        ProductCost.product_id==int(product_id),
        sqlalchemy.sql.expression.cast(sqlalchemy.func.daterange(
            ProductCost.start_date,
            ProductCost.end_date
        ), sqlalchemy.dialects.postgresql.DATERANGE).contains(cost_date)
    ).order_by(
        sqlalchemy.desc(ProductCost.end_date).nullsfirst(),
    ).first()
    return product_cost


def process_orders(orders):
    rows = []
    for order in orders:
        customer = order.get('customer')
        lines = order.get('line_items')
        tax_lines = order.get('tax_lines')
        discount_value = decimal.Decimal(order.get('total_discounts'))
        row = {
            'order_no': order.get('name'),
            'customer_firstname': customer.get('first_name'),
            'customer_lastname': customer.get('last_name'),
            'customer_email': customer.get('email'),
            'products': [],
            'excluding_taxes_amount': 0,
            'discount_amount': 0,
            'cost_amount': 0,
            'benefits': 0,
        }
        for line in lines:
            product_id = line.get('product_id')
            product_cost = None
            if product_id:
                product_id = int(line.get('product_id'))
                product_cost = current_product_cost(product_id)
            row['cost_amount'] += product_cost.value if product_cost else 0
            taxes = line.get('tax_lines')
            row['products'].append(line.get('title'))
            price = decimal.Decimal(line.get('price'))
            if order.get('taxes_included'):
                for tax_line in taxes:
                    tax_rate = decimal.Decimal(tax_line.get('rate'))
                    row['excluding_taxes_amount'] += price / (1 + tax_rate)
            else:
                row['excluding_taxes_amount'] += price
        if order.get('taxes_included'):
            for tax_line in tax_lines:
                tax_rate = decimal.Decimal(tax_line.get('rate'))
                row['discount_amount'] += discount_value / (1 + tax_rate)
        else:
            row['discount_amount'] += discount_value
        row['benefits'] = row['excluding_taxes_amount'] - row['discount_amount'] - row['cost_amount']
        rows.append(row)
    return rows


def request_wants_json():
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes['text/html']
