# -*- coding: utf-8 -*-

from datetime import datetime
from tabapp.models import db
from sqlalchemy.orm import relationship, backref


class Invoice(db.Model):
    __tablename__ = 'invoice'
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    version = db.Column(db.DateTime, nullable=False, default=datetime.now())
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    retailer_id = db.Column(db.Integer, db.ForeignKey('retailer.id'))
    retailer = relationship('Retailer', backref=backref('invoices', lazy='dynamic'))
    no = db.Column(db.String)
