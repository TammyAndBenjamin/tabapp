# -*- coding: utf-8 -*-

from datetime import datetime
from flask import Blueprint, render_template, request, g, current_app, abort
from flask.ext.login import login_required
from tabapp.models import db, Url
import hashlib

urls_bp = Blueprint('urls_bp', __name__, subdomain='backyard')


@urls_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        long_url = request.form['long_url']
        if not long_url[:4] == 'http':
            long_url = 'http://{}'.format(long_url)
        m = hashlib.sha256()
        m.update(datetime.now().isoformat().encode())
        m.update(long_url.encode())
        url = Url()
        url.long_url = long_url
        url.uuid = m.hexdigest()[:5]
        db.session.add(url)
        db.session.commit()
    urls = Url.query.all()
    context = {
        'urls': urls,
    }
    return render_template('urls/list.html', **context)


@urls_bp.route('/<int:url_id>/')
@login_required
def one(url_id):
    url = Url.query.get(url_id)
    if not url:
        return abort(404)
    context = {}
    return render_template('urls/url.html', **context)

