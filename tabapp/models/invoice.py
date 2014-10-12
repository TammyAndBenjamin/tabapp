# -*- coding: utf-8 -*-

import sqlalchemy
from datetime import datetime
from tabapp.models import db, InvoiceItem
from sqlalchemy.orm import relationship, backref
from sqlalchemy_utils import aggregated


class Invoice(db.Model):
    __tablename__ = 'invoice'
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    version = db.Column(db.DateTime, nullable=False, default=datetime.now())
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    retailer_id = db.Column(db.Integer, db.ForeignKey('retailer.id'))
    retailer = relationship('Retailer', backref=backref('invoices', lazy='dynamic'))
    no = db.Column(db.String)

    @aggregated('items', db.Column(db.Numeric))
    def excl_tax_price(self):
        return sqlalchemy.func.sum(InvoiceItem.excl_tax_price)

    @aggregated('items', db.Column(db.Numeric))
    def tax_price(self):
        return sqlalchemy.func.sum(InvoiceItem.tax_price)

    @aggregated('items', db.Column(db.Numeric))
    def incl_tax_price(self):
        return sqlalchemy.func.sum(InvoiceItem.incl_tax_price)
