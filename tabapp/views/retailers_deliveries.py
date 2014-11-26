# -*- coding: utf-8 -*-

from datetime import date
from flask import Blueprint, request, render_template,\
    redirect, url_for, flash, current_app, jsonify, abort, g
from flask.ext.login import login_required
from tabapp.models import db, Invoice, Retailer, Product,\
    RetailerProduct, DeliverySlip, DeliverySlipLine
import tabapp.utils
import decimal
import math
import sqlalchemy
import sqlalchemy.dialects.postgresql


bp_name = 'retailers_deliveries_bp'
retailers_deliveries_bp = Blueprint(bp_name, __name__, subdomain='backyard')


def tab_counts(retailer):
    counts = {
        'delivery_slips': DeliverySlip.query.filter(
            DeliverySlip.retailer_id == retailer.id
        ).count(),
        'stocks': RetailerProduct.query.filter(
            RetailerProduct.retailer_id == retailer.id,
            RetailerProduct.sold_date.is_(None)
        ).count(),
        'sold': RetailerProduct.query.filter(
            RetailerProduct.retailer_id == retailer.id,
            RetailerProduct.sold_date.isnot(None),
            RetailerProduct.invoice_item_id.is_(None)
        ).count(),
        'invoices': Invoice.query.filter(
            Invoice.retailer_id == retailer.id
        ).count(),
    }
    return counts


@retailers_deliveries_bp.route('/<int:retailer_id>/delivery_slips/')
@login_required
def index(retailer_id):
    retailer = Retailer.query.get(retailer_id)
    context = {
        'retailer': retailer,
        'delivery_slips': DeliverySlip.query.filter(
                DeliverySlip.retailer_id == retailer.id
            ).order_by(DeliverySlip.delivery_date),
        'tab_counts': tab_counts(retailer),
    }
    return render_template('retailers/delivery_slips.html', **context)


@retailers_deliveries_bp.route('/<int:retailer_id>/delivery_slips/add', methods=['GET', 'POST'])
@login_required
def add(retailer_id):
    retailer = Retailer.query.get(retailer_id)
    if request.method == 'POST':
        try:
            product_ids = [int(v) for v in request.form.getlist('product_id')]
            quantities = [int(v) for v in request.form.getlist('quantity')]
            cart = zip(product_ids, quantities)
            delivery_slip = DeliverySlip()
            db.session.add(delivery_slip)
            delivery_slip.retailer_id = retailer.id
            for product_id, quantity in cart:
                if not quantity:
                    continue
                product = Product.query.get(product_id)
                retailer_unit_price = product.unit_price * (1 - retailer.fees_proportion)
                delivery_slip_line = DeliverySlipLine()
                delivery_slip_line.product_id = product.id
                delivery_slip_line.fees = retailer.fees_proportion
                delivery_slip_line.quantity = delivery_slip_line.orders.count()
                for i in range(quantity):
                    retailer_product = RetailerProduct()
                    retailer_product.retailer_id = retailer.id
                    retailer_product.product_id = product_id
                    retailer_product.order_date = date.today()
                    retailer.stocks.append(retailer_product)
                    delivery_slip_line.orders.append(retailer_product)
                delivery_slip_line.quantity = quantity
                delivery_slip_line.recommanded_price = product.unit_price
                delivery_slip_line.excl_tax_price = retailer_unit_price * delivery_slip_line.quantity
                delivery_slip_line.incl_tax_price = delivery_slip_line.excl_tax_price * g.config['APP_VAT']
                delivery_slip_line.tax_price = delivery_slip_line.incl_tax_price - delivery_slip_line.excl_tax_price
                delivery_slip.lines.append(delivery_slip_line)
                product = Product.query.get(product_id)
                product.quantity = product.quantity - quantity
                remote_url = '{}variants/{{}}.json'.format(g.config['SHOPIFY_URL'])
                product.push_to_remote(remote_url, quantity * -1)
            db.session.commit()
            kwargs = {
                'retailer_id': retailer_id,
            }
            return redirect(url_for('retailers_deliveries_bp.index', **kwargs))
        except Exception as e:
            db.session.rollback()
            for msg in e.args:
                flash(msg, 'error')
    page = int(request.args.get('page', 1))
    products = Product.query.filter(Product.quantity > 0).order_by(Product.title).paginate(page, per_page=12)
    context = {
        'retailer': retailer,
        'tab_counts': tab_counts(retailer),
        'products': products.items,
        'page': products.page,
        'max_page': products.pages,
    }
    return render_template('retailers/products.html', **context)


@retailers_deliveries_bp.route('/<int:retailer_id>/delivery_slips/<int:delivery_slip_id>/')
@login_required
def one(retailer_id, delivery_slip_id):
    retailer = Retailer.query.get(retailer_id)
    delivery_slip = DeliverySlip.query.get(delivery_slip_id)
    products_count = sum([line.quantity for line in delivery_slip.lines])
    context = {
        'retailer': retailer,
        'delivery_slip': delivery_slip,
        'products_count': products_count,
    }
    return render_template('retailers/delivery_slip.html', **context)
