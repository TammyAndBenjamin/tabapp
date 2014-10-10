# -*- coding: utf-8 -*-

from flask import Blueprint, request, render_template, jsonify, g, current_app, redirect, url_for
from flask.ext.login import login_required
from tabapp.models import db, Product
from datetime import datetime, date
import tabapp.utils
import math
import sqlalchemy
import sqlalchemy.sql.expression
import sqlalchemy.dialects.postgresql


products_bp = Blueprint('products_bp', __name__, subdomain='backyard')


@products_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1)
    products = Product.query.paginate(page)
    context = {
        'products': products.items,
        'page': products.page,
        'max_page': products.pages,
    }
    return render_template('products/list.html', **context)


@products_bp.route('/sync', methods=['POST'])
@login_required
def sync():
    Product.sync_from_remote()
    return redirect(url_for('products_bp.index'))
