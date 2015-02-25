# -*- coding: utf-8 -*-

from sqlalchemy.sql.expression import func
from tabapp.models import db
from sqlalchemy.orm import relationship, backref

RetailerContact = db.Table('retailer_contact',
    db.Column('id', db.Integer, db.Sequence('core_seq_general'), primary_key=True),
    db.Column('created', db.DateTime, nullable=False, default=func.now()),
    db.Column('version', db.DateTime, nullable=False, default=func.now(), onupdate=func.now()),
    db.Column('enabled', db.Boolean, nullable=False, default=True),
    db.Column('retailer_id', db.Integer, db.ForeignKey('retailer.id'), nullable=False),
    db.Column('contact_id', db.Integer, db.ForeignKey('contact.id', ondelete='CASCADE'), nullable=False)
)

class Retailer(db.Model):
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=func.now())
    version = db.Column(db.DateTime, nullable=False, default=func.now(), onupdate=func.now())
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    name = db.Column(db.String, nullable=False)
    code = db.Column(db.String, nullable=False)
    fees_proportion = db.Column(db.Numeric, nullable=False)
    address = db.Column(db.String)
    zip = db.Column(db.String)
    city = db.Column(db.String)
    country = db.Column(db.String)
    contacts = relationship('Contact', secondary='retailer_contact', backref=backref('retailers', lazy='dynamic'))
