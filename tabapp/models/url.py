# -*- coding: utf-8 -*-

from sqlalchemy.sql.expression import func
from sqlalchemy.orm import relationship, backref
from tabapp.models import db
import sqlalchemy_utils

class Url(db.Model):
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=func.now())
    version = db.Column(db.DateTime, nullable=False, default=func.now(), onupdate=func.now())
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    long_url = db.Column(sqlalchemy_utils.URLType, nullable=False)
    uuid = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=func.now())

class UrlClick(db.Model):
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=func.now())
    version = db.Column(db.DateTime, nullable=False, default=func.now(), onupdate=func.now())
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    ip_address = db.Column(sqlalchemy_utils.IPAddressType)
    url_id = db.Column(db.Integer, db.ForeignKey('url.id'))
    url = relationship('Url', backref=backref('clicks', lazy='dynamic'))
