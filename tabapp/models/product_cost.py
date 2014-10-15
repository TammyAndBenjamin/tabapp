# -*- coding: utf-8 -*-

from datetime import datetime
from tabapp.models import db
from sqlalchemy.orm import relationship, backref


class ProductCost(db.Model):
    __tablename__ = 'product_cost'
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    version = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now)
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product = relationship('Product', backref=backref('costs', lazy='dynamic'), order_by='desc(ProductCost.end_date).nullsfirst(), desc(ProductCost.start_date)')
    value = db.Column(db.Numeric)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
