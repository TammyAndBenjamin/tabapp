# -*- coding: utf-8 -*-

import sqlalchemy_utils
from datetime import datetime
from tabapp.models import db
from sqlalchemy.orm import relationship, backref

class Login(db.Model):
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    version = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    username = db.Column(db.String, index = True, unique = True)
    password = db.Column(sqlalchemy_utils.PasswordType(
        schemes=[
            'pbkdf2_sha512',
        ],
    ))
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    contact = relationship('Contact', backref=backref('logins', lazy='dynamic'))


    def is_authenticated(self):
        return bool(self.id)


    def is_active(self):
        return bool(self.id)


    def is_anonymous(self):
        return not bool(self.id)


    def get_id(self):
        return str(self.id)
