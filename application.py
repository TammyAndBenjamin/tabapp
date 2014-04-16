#!/usr/bin/env python                                                                                                                                                                                                                                                         [98/217]
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals
from flask import Flask, request, render_template, jsonify
from flask_wtf.csrf import CsrfProtect
from form_order import OrderForm, ItemLine
import json
import requests

key = '3adfb09ddcdbafd4851e294634b8af9a'
pwd = '9f67e06ae055c0c11dba39df4650d0ff'
base_url = 'https://{}:{}@tammyandbenjamin.myshopify.com/admin/'.format(key, pwd)

app = Flask(__name__)
CsrfProtect(app)

def list_from_api(url, key, page = None):
    def make_requests(url, page):
        url = url.format(**{'page': page})
        r = requests.get(url)
        return r.json()
    if page:
        data = make_requests(url, page)
        rows = data.get(key)
    else:
        page = 1
        rows = []
        while True:
            data = make_requests(url, page)
            if not data.get(key):
                break
            rows += data.get(key)
            page += 1
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
            row['subtotal_price'] += (float(order.get('total_price', 0)) - float(order.get('total_tax', 0)))
        else:
            row['subtotal_price'] += float(order.get('subtotal_price', 0))
        row['total_discount'] += float(order.get('total_discount', 0))
        row['total_tax'] += float(order.get('total_tax', 0))
        row['total_price'] += float(order.get('total_price', 0))
        aggregate[customer_email] = row
    return aggregate

def process_orders(orders):
    rows = []
    for order in orders:
        customer = order.get('customer')
        lines = order.get('line_items')
        tax_lines = order.get('tax_lines')
        discount_value = float(order.get('total_discounts'))
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
            taxes = line.get('tax_lines')
            row['products'].append(line.get('title'))
            price = float(line.get('price'))
            if order.get('taxes_included'):
                for tax_line in taxes:
                    tax_rate = float(tax_line.get('rate'))
                    row['excluding_taxes_amount'] += price / (1 + tax_rate)
            else:
                row['excluding_taxes_amount'] += price
        if order.get('taxes_included'):
            for tax_line in tax_lines:
                tax_rate = float(tax_line.get('rate'))
                row['discount_amount'] += discount_value / (1 + tax_rate)
        else:
            row['discount_amount'] += discount_value
        row['benefits'] = row['excluding_taxes_amount'] - row['discount_amount'] - row['cost_amount']
        rows.append(row)
    return rows

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analytics')
def analytics():
    date_lbound = request.args.get('date_lbound')
    date_ubound = request.args.get('date_ubound')
    fields = [
        'name',
        'created_at',
        'customer',
        'tags',
        'line_items',
        'taxes_included',
        'tax_lines',
        'total_discounts',
    ]
    url = '{base_url}orders.json?page={{page}}&fields={fields}{date_lbound}{date_ubound}'.format(**{
            'base_url': base_url,
            'fields': ','.join(fields),
            'date_lbound': '&updated_at_min={}'.format(date_lbound) if date_lbound else '',
            'date_ubound': '&updated_at_max={}'.format(date_ubound) if date_ubound else '',
        })
    orders = list_from_api(url, 'orders')
    rows = process_orders(orders)
    return jsonify(rows=rows)

@app.route('/orders/', defaults={'page': 1})
@app.route('/orders/<int:page>')
def orders(page):
    url = '{base_url}orders.json?page={{page}}'.format(**{
            'base_url': base_url,
        })
    orders = list_from_api(url, 'orders', page)
    return render_template('orders.html', orders=orders)


if __name__ == "__main__":
    app.run(host='172.16.1.55',debug=True)
