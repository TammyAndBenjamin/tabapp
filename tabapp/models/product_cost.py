# -*- coding: utf-8 -*-

from sqlalchemy.sql.expression import func
from sqlalchemy.orm import relationship, backref
from tabapp.models import db


class ProductCost(db.Model):
    __tablename__ = 'product_cost'
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=func.now())
    version = db.Column(db.DateTime, nullable=False, default=func.now(), onupdate=func.now())
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product = relationship('Product', backref=backref('costs', lazy='dynamic'), order_by='desc(ProductCost.end_date).nullsfirst(), desc(ProductCost.start_date)')
    value = db.Column(db.Numeric)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
