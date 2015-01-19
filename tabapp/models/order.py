# -*- coding: utf-8 -*-

from datetime import datetime
from tabapp.models import db
from sqlalchemy.dialects.postgresql import ARRAY


class ProductOrder(db.Model):
    __tablename__ = 'product_order'
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    version = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    remote_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String, nullable=False)
    shipping_country = db.Column(db.String, nullable=False)
    date = db.Column(db.Date, nullable=False)
    financial_status = db.Column(db.String, nullable=False)
    subtotal_price = db.Column(db.Numeric, nullable=False)
    total_tax = db.Column(db.Numeric, nullable=False)
    total_price = db.Column(db.Numeric, nullable=False)
    transaction_ids = db.Column(ARRAY(db.Integer), nullable=False)
    paid_price = db.Column(db.Numeric, nullable=False)
    refunded_price = db.Column(db.Numeric, nullable=False)
