# -*- coding: utf-8 -*-

from sqlalchemy.sql.expression import func
from sqlalchemy.orm import relationship
from tabapp.models import db
import sqlalchemy_utils

ContactRole = db.Table('contact_role',
    db.Column('id', db.Integer, db.Sequence('core_seq_general'), primary_key=True),
    db.Column('created', db.DateTime, nullable=False, default=func.now()),
    db.Column('version', db.DateTime, nullable=False, default=func.now(), onupdate=func.now()),
    db.Column('enabled', db.Boolean, nullable=False, default=True),
    db.Column('contact_id', db.Integer, db.ForeignKey('contact.id', ondelete='CASCADE'), nullable=False),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id', ondelete='CASCADE'), nullable=False)
)


class Contact(db.Model):
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=func.now())
    version = db.Column(db.DateTime, nullable=False, default=func.now(), onupdate=func.now())
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    firstname = db.Column(db.String, nullable=False)
    lastname = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    phone = db.Column(db.String())
    username = db.Column(db.String, index=True, unique=True)
    password = db.Column(sqlalchemy_utils.PasswordType(
        schemes=[
            'pbkdf2_sha512',
        ],
    ))
    roles = relationship('Role', secondary='contact_role')

    def is_authenticated(self):
        return bool(self.id)


    def is_active(self):
        return bool(self.id)


    def is_anonymous(self):
        return not bool(self.id)


    def get_id(self):
        return str(self.id)
