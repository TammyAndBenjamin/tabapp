# -*- coding: utf-8 -*-

from datetime import date
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for, flash, jsonify, g
)
from flask.ext.login import login_required
from flask.ext.babel import gettext as _
from tabapp.models import (
    db, Invoice, Retailer, Product,
    RetailerProduct, DeliverySlip, Contact
)
import tabapp.utils


bp_name = 'retailers_stocks_bp'
retailers_stocks_bp = Blueprint(bp_name, __name__, subdomain='backyard')


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
        'contacts': len(retailer.contacts),
    }
    return counts


@retailers_stocks_bp.route('/<int:retailer_id>/stocks/', methods=['GET'])
@login_required
def index(retailer_id):
    retailer = Retailer.query.get(retailer_id)
    context = {
        'retailer': retailer,
        'stocks': retailer.stocks.filter(RetailerProduct.sold_date.is_(None)),
        'tab_counts': tab_counts(retailer),
    }
    return render_template('retailers/stocks.html', **context)


@retailers_stocks_bp.route('/<int:retailer_id>/stocks/<int:retailer_product_id>/sell', methods=['POST'])
@login_required
def sell(retailer_id, retailer_product_id):
    retailer = Retailer.query.get(retailer_id)
    retailer_product = RetailerProduct.query.get(retailer_product_id)
    if not retailer or not retailer_product or retailer.id != retailer_product.retailer_id:
        return abort(404)
    retailer_product.sold_date = date.today()
    db.session.commit()
    if tabapp.utils.request_wants_json():
        return jsonify(success=_('Product sold.'), tab_counts=tab_counts(retailer))
    flash(_('Product sold.'), 'success')
    kwargs = {
        'retailer_id': retailer.id,
    }
    return redirect(url_for('retailers_stocks_bp.index', **kwargs))


@retailers_stocks_bp.route('/<int:retailer_id>/stocks/<int:retailer_product_id>/', methods=['DELETE'])
@login_required
def delete(retailer_id, retailer_product_id):
    retailer = Retailer.query.get(retailer_id)
    retailer_product = RetailerProduct.query.get(retailer_product_id)
    if not retailer or not retailer_product or retailer.id != retailer_product.retailer_id:
        return abort(404)
    try:
        db.session.delete(retailer_product)
        product = Product.query.get(retailer_product.product_id)
        product.quantity = product.quantity + 1
        remote_url = '{}variants/{{}}.json'.format(g.config['SHOPIFY_URL'])
        product.push_to_remote(remote_url, 1)
        db.session.commit()
        if tabapp.utils.request_wants_json():
            return jsonify(success=_('Product deleted from stocks.'), tab_counts=tab_counts(retailer))
        flash(_('Product deleted from stocks.'), 'success')
    except Exception as e:
        db.session.rollback()
        for msg in e.args:
            flash(msg, 'error')
    kwargs = {
        'retailer_id': retailer.id,
    }
    return redirect(url_for('retailers_stocks_bp.index', **kwargs))
