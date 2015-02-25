# -*- coding: utf-8 -*-

from sqlalchemy.sql.expression import func
from tabapp.models import db


class Lead(db.Model):
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=func.now())
    version = db.Column(db.DateTime, nullable=False, default=func.now(), onupdate=func.now())
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    firstname = db.Column(db.String)
    lastname = db.Column(db.String)
    email = db.Column(db.String, nullable=False)
    phone = db.Column(db.String())
    in_list = db.Column(db.Boolean(), default=False)
