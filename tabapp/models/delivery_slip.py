# -*- coding: utf-8 -*-

from datetime import datetime, date
from tabapp.models import db
from sqlalchemy.orm import relationship, backref
from sqlalchemy_utils import aggregated
import sqlalchemy


def generate_no(context):
    today = date.today()
    return 'BD{}{}{}'.format(today.year, today.month, today.day)


class DeliverySlip(db.Model):
    __tablename__ = 'delivery_slip'
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    version = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now)
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    retailer_id = db.Column(db.Integer, db.ForeignKey('retailer.id'), nullable=False)
    retailer = relationship('Retailer')
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = relationship('Product')
    no = db.Column(db.String, nullable=False, default=generate_no)
    delivery_date = db.Column(db.Date, nullable=False, default=date.today())

    @aggregated('orders', db.Column(db.Integer))
    def quantity(self):
        return sqlalchemy.func.count(DeliverySlip.orders)
