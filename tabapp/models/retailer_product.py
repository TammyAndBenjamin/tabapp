# -*- coding: utf-8 -*-

from sqlalchemy.sql.expression import func
from sqlalchemy.orm import relationship, backref
from tabapp.models import db


class RetailerProduct(db.Model):
    __tablename__ = 'retailer_product'
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=func.now())
    version = db.Column(db.DateTime, nullable=False, default=func.now(), onupdate=func.now())
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = relationship('Product', backref=backref('stocks', lazy='dynamic'))
    retailer_id = db.Column(db.Integer, db.ForeignKey('retailer.id'), nullable=False)
    retailer = relationship('Retailer', backref=backref('stocks', lazy='dynamic'))
    order_date = db.Column(db.Date)
    sold_date = db.Column(db.Date)
    invoice_item_id = db.Column(db.Integer, db.ForeignKey('invoice_item.id'))
    invoice_item = relationship('InvoiceItem', backref=backref('orders', lazy='dynamic'))
    delivery_slip_line_id = db.Column(db.Integer, db.ForeignKey('delivery_slip_line.id'))
    delivery_slip_line = relationship('DeliverySlipLine', backref=backref('orders', lazy='dynamic'))
