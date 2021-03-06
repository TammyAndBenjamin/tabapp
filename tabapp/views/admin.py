# -*- coding: utf-8 -*-

from flask import Blueprint, render_template
from tabapp.extensions.security import permisssion_required

admin_bp = Blueprint('admin_bp', __name__, subdomain='backyard')


@admin_bp.route('/')
@permisssion_required(['admin'])
def index():
    return render_template('admin/index.html')
