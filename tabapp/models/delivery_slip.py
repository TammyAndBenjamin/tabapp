# -*- coding: utf-8 -*-

from datetime import datetime, date
from tabapp.models import db, DeliverySlipLine
from sqlalchemy.orm import relationship, backref
from sqlalchemy_utils import aggregated
import sqlalchemy


def generate_no(context):
    today = date.today()
    idx = DeliverySlip.query.filter(DeliverySlip.delivery_date == today).count()
    return 'BD{}{:02d}{:02d}{:03d}'.format(today.year, today.month, today.day, idx + 1)


class DeliverySlip(db.Model):
    __tablename__ = 'delivery_slip'
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    version = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    retailer_id = db.Column(db.Integer, db.ForeignKey('retailer.id'), nullable=False)
    retailer = relationship('Retailer')
    delivery_date = db.Column(db.Date, nullable=False, default=date.today)
    no = db.Column(db.String, nullable=False, default=generate_no)

    @aggregated('lines', db.Column(db.Numeric))
    def excl_tax_price(self):
        return sqlalchemy.func.sum(DeliverySlipLine.excl_tax_price)

    @aggregated('lines', db.Column(db.Numeric))
    def tax_price(self):
        return sqlalchemy.func.sum(DeliverySlipLine.tax_price)

    @aggregated('lines', db.Column(db.Numeric))
    def incl_tax_price(self):
        return sqlalchemy.func.sum(DeliverySlipLine.incl_tax_price)
