# -*- coding: utf-8 -*-

from datetime import datetime
from tabapp.models import db
from sqlalchemy.orm import relationship, backref


class InvoiceItem(db.Model):
    __tablename__ = 'invoice_item'
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    version = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'))
    invoice = relationship('Invoice', backref=backref('items', lazy='dynamic'))
    title = db.Column(db.String)
    unit_price = db.Column(db.Numeric)
    quantity = db.Column(db.Integer)
    excl_tax_price = db.Column(db.Numeric)
    tax_price = db.Column(db.Numeric)
    incl_tax_price = db.Column(db.Numeric)
