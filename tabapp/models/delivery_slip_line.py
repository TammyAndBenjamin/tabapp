# -*- coding: utf-8 -*-

from datetime import datetime
from tabapp.models import db
from sqlalchemy.orm import relationship, backref
from sqlalchemy_utils import aggregated
import sqlalchemy


class DeliverySlipLine(db.Model):
    __tablename__ = 'delivery_slip_line'
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    version = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    delivery_slip_id = db.Column(db.Integer, db.ForeignKey('delivery_slip.id'))
    delivery_slip = relationship('DeliverySlip', backref=backref('lines', lazy='dynamic'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product = relationship('Product')
    recommanded_price = db.Column(db.Numeric, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    fees = db.Column(db.Numeric, nullable=False)
    excl_tax_price = db.Column(db.Numeric, nullable=False)
    tax_price = db.Column(db.Numeric, nullable=False)
    incl_tax_price = db.Column(db.Numeric, nullable=False)
