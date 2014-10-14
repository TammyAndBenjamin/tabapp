# -*- coding: utf-8 -*-

from datetime import datetime
from tabapp.models import db

class Retailer(db.Model):
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    version = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now)
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    name = db.Column(db.String, nullable=False)
    fees_proportion = db.Column(db.Numeric, nullable=False)
    address = db.Column(db.String)
    zip = db.Column(db.String)
    city = db.Column(db.String)
    country = db.Column(db.String)
    contact_firstname = db.Column(db.String)
    contact_lastname = db.Column(db.String)
