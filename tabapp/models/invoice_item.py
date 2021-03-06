# -*- coding: utf-8 -*-

from sqlalchemy.sql.expression import func
from sqlalchemy.orm import relationship, backref
from sqlalchemy_utils import aggregated
from tabapp.models import db
import sqlalchemy


class InvoiceItem(db.Model):
    __tablename__ = 'invoice_item'
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=func.now())
    version = db.Column(db.DateTime, nullable=False, default=func.now(), onupdate=func.now())
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'))
    invoice = relationship('Invoice', backref=backref('items', lazy='dynamic'))
    title = db.Column(db.String)
    unit_price = db.Column(db.Numeric)
    excl_tax_price = db.Column(db.Numeric)
    tax_price = db.Column(db.Numeric)
    incl_tax_price = db.Column(db.Numeric)

    @aggregated('orders', db.Column(db.Integer))
    def quantity(self):
        return sqlalchemy.func.count(InvoiceItem.orders)
