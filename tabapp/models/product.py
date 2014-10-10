# -*- coding: utf-8 -*-

from datetime import datetime
from tabapp.models import db


class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    version = db.Column(db.DateTime, nullable=False, default=datetime.now())
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    title = db.Column(db.String, nullable=False)
    quantity = db.Column(db.Integer)
    unit_price = db.Column(db.Numeric)
    image = db.Column(db.String)
    remote_id = db.Column(db.Integer, nullable=False)
    last_sync = db.Column(db.DateTime, nullable=False, default=datetime.now())
