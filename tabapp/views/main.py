# -*- coding: utf-8 -*-


from flask import Blueprint, render_template
from flask.ext.login import login_required


main_bp = Blueprint('main_bp', __name__, subdomain='backyard')


@main_bp.route('/')
@login_required
def index():
    return render_template('index.html')
