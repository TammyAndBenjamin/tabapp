# -*- coding: utf-8 -*-

from datetime import datetime
from tabapp.models import db
from sqlalchemy.orm import relationship, backref


class RetailerProduct(db.Model):
    __tablename__ = 'retailer_product'
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    version = db.Column(db.DateTime, nullable=False, default=datetime.now())
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    retailer_id = db.Column(db.Integer, db.ForeignKey('retailer.id'))
    retailer = relationship('Retailer', backref=backref('stocks', lazy='dynamic'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product = relationship('Product')
    order_date = db.Column(db.Date)
    sold_date = db.Column(db.Date)
    payment_date = db.Column(db.Date)
