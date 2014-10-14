# -*- coding: utf-8 -*-

from datetime import datetime
from tabapp.models import db
from sqlalchemy.orm import relationship, backref


class RetailerProduct(db.Model):
    __tablename__ = 'retailer_product'
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    version = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now)
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product = relationship('Product')
    retailer_id = db.Column(db.Integer, db.ForeignKey('retailer.id'))
    retailer = relationship('Retailer', backref=backref('stocks', lazy='dynamic'))
    order_date = db.Column(db.Date)
    sold_date = db.Column(db.Date)
    invoice_item_id = db.Column(db.Integer, db.ForeignKey('invoice_item.id'))
    invoice_item = relationship('InvoiceItem', backref=backref('orders', lazy='dynamic'))
