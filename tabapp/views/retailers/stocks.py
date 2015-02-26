# -*- coding: utf-8 -*-

from datetime import date
from flask import (
    Blueprint,
    render_template,
    redirect, abort,
    url_for, flash, jsonify, g
)
from flask.ext.babel import gettext as _
from tabapp.models import db, Retailer, Product, RetailerProduct
from tabapp.views.retailers import tab_counts
from tabapp.extensions.security import permisssion_required
import tabapp.utils


bp_name = 'retailers_stocks_bp'
retailers_stocks_bp = Blueprint(bp_name, __name__, subdomain='backyard')


@retailers_stocks_bp.route('/<int:retailer_id>/stocks/', methods=['GET'])
@permisssion_required(['normal', 'retailer'])
def index(retailer_id):
    permisssion = Permission(RoleNeed('normal'))
    need = ItemNeed('access', 'retailer', retailer_id)
    if not permisssion.union(Permission(need)).can():
        return abort(403)
    retailer = Retailer.query.get(retailer_id)
    context = {
        'retailer': retailer,
        'stocks': retailer.stocks.filter(RetailerProduct.sold_date.is_(None)),
        'tab_counts': tab_counts(retailer),
    }
    return render_template('retailers/stocks.html', **context)


@retailers_stocks_bp.route('/<int:retailer_id>/stocks/<int:retailer_product_id>/sell', methods=['POST'])
@permisssion_required(['normal', 'retailer'])
def sell(retailer_id, retailer_product_id):
    permisssion = Permission(RoleNeed('normal'))
    need = ItemNeed('access', 'retailer', retailer_id)
    if not permisssion.union(Permission(need)).can():
        return abort(403)
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
@permisssion_required(['normal'])
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
