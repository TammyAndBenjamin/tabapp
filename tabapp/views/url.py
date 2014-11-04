# -*- coding: utf-8 -*-

from flask import Blueprint, request, redirect, abort
from tabapp.models import db, Url, UrlClick
from tabapp.utils import noindex

url_bp = Blueprint('url_bp', __name__, subdomain='data')


@url_bp.route('/<uuid>/')
@noindex
def u(uuid):
    url = Url.query.filter(Url.uuid==uuid).first()
    if not url:
        return abort(404)
    url_click = UrlClick()
    url_click.ip_address = request.remote_addr
    url.clicks.append(url_click)
    db.session.commit()
    return redirect(url.long_url)
