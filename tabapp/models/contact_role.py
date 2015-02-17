# -*- coding: utf-8 -*-

from datetime import datetime
from tabapp.models import db


class ContactRole(db.Model):
    __tablename__ = 'contact_role'
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    version = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
