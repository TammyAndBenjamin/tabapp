#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals
from flask import Flask, request, render_template, jsonify
import requests

key = '3adfb09ddcdbafd4851e294634b8af9a'
pwd = '9f67e06ae055c0c11dba39df4650d0ff'
base_url = 'https://{}:{}@tammyandbenjamin.myshopify.com/admin/'.format(key, pwd)

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/orders")
def orders():
    date_lbound = request.args.get('date_lbound')
    date_ubound = request.args.get('date_ubound')
    groupby = request.args.get('groupby')
    fields = [
        'created_at',
        'customer',
        'tags',
        'line_items',
    ]
    url = '{base_url}orders.json?financial_status=paid&fields={fields}{date_lbound}{date_ubound}'.format(**{
            'base_url': base_url,
            'fields': ','.join(fields),
            'date_lbound': '&updated_at_min={}'.format(date_lbound) if date_lbound else '',
            'date_ubound': '&updated_at_max={}'.format(date_ubound) if date_ubound else '',
        })
    r = requests.get(url)
    orders = r.json()
    aggregate = {}
    for order in orders:
        pass
    return jsonify(orders)

if __name__ == "__main__":
    app.run(host='172.16.1.55',debug=True)
