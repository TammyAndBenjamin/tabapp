# -*- coding: utf-8 -*-

from sqlalchemy.sql.expression import func
from sqlalchemy.orm import relationship, backref
from sqlalchemy_utils import aggregated
from tabapp.models import db
import sqlalchemy


class DeliverySlipLine(db.Model):
    __tablename__ = 'delivery_slip_line'
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=func.now())
    version = db.Column(db.DateTime, nullable=False, default=func.now(), onupdate=func.now())
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
