# -*- coding: utf-8 -*-

from datetime import date
from dateutil.relativedelta import relativedelta
from flask import Blueprint, request, render_template
from flask.ext.login import login_required
from form_order import OrderForm
from utils import list_from_resource, process_orders
import math

orders_bp = Blueprint('orders_bp', __name__, subdomain='backyard')

@orders_bp.route('/', defaults={'page': 1})
@orders_bp.route('/<int:page>')
@login_required
def index(page):
    default_lbound = date.today() - relativedelta(months=1)
    default_ubound = date.today()
    date_lbound = request.args.get('date_lbound', default_lbound)
    date_ubound = request.args.get('date_ubound', default_ubound)
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
    resource = 'orders'
    params = '?financial_status=paid&page={{page}}&fields={fields}{date_lbound}{date_ubound}'.format(**{
            'fields': ','.join(fields),
            'date_lbound': '&updated_at_min={}'.format(date_lbound) if date_lbound else '',
            'date_ubound': '&updated_at_max={}'.format(date_ubound) if date_ubound else '',
        })
    max_page = math.ceil(list_from_resource(resource, params, count = True) / 50)
    orders = list_from_resource(resource, params, page)
    orders = process_orders(orders)
    context = {
        'page': page,
        'date_lbound': date_lbound,
        'date_ubound': date_ubound,
        'max_page': max_page,
        'orders': orders,
    }
    return render_template('orders.html', **context)

@orders_bp.route('/add')
@login_required
def form():
    form = OrderForm(request.form)
    return render_template('order.html', form=form)
