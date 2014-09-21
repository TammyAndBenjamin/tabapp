# -*- coding: utf-8 -*-

from functools import wraps
from flask import g, make_response
import decimal
import requests
import psycopg2.extras


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


def list_from_resource(resource, params, limit = None, page = None, count = False):
    def make_requests(url, page, limit):
        url = url.format(**{'page': page, 'limit': limit})
        r = requests.get(url)
        return r.json()
    if not limit:
        limit = 50
    url = '{}{}.json{}'.format(g.config['SHOPIFY_URL'], resource, params)
    if count:
        url = url.replace(resource, '{}/count'.format(resource))
        data = make_requests(url, 1, limit)
        return int(data.get('count'))
    if page:
        data = make_requests(url, page, limit)
        rows = data.get(resource.split('/')[0])
    else:
        page = 1
        rows = []
        while True:
            data = make_requests(url, page, limit)
            result = data.get(resource.split('/')[0])
            if not result:
                break
            rows += result
            page += 1
    return rows


def process_orders(orders):
    cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
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
            cur.execute('''
                SELECT value
                FROM product_cost
                WHERE product_id = %s
                AND daterange(start_date, end_date) @> current_date
            ''', (int(line.get('product_id')), ))
            cost_row = cur.fetchone()
            row['cost_amount'] += cost_row.get('value', 0) if cost_row else 0
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


def aggregate_orders(orders):
    aggregate = {}
    for order in orders:
        customer = order.get('customer')
        customer_email = customer.get('email')
        row = aggregate.get(customer_email)
        if not row:
            row = {
                'count': 0,
                'subtotal_price': 0,
                'total_discount': 0,
                'total_tax': 0,
                'total_price': 0,
            }
        row['count'] += 1
        if order.get('taxes_included'):
            row['subtotal_price'] += (decimal.Decimal(order.get('total_price', 0)) - decimal.Decimal(order.get('total_tax', 0)))
        else:
            row['subtotal_price'] += decimal.Decimal(order.get('subtotal_price', 0))
        row['total_discount'] += decimal.Decimal(order.get('total_discount', 0))
        row['total_tax'] += decimal.Decimal(order.get('total_tax', 0))
        row['total_price'] += decimal.Decimal(order.get('total_price', 0))
        aggregate[customer_email] = row
    return aggregate
