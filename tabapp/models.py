# -*- coding: utf-8 -*-

import sqlalchemy_utils
from datetime import datetime
from tabapp import db


class Login(db.Model):
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    version = db.Column(db.DateTime, nullable=False, default=datetime.now())
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    username = db.Column(db.String, index = True, unique = True)
    password = db.Column(sqlalchemy_utils.PasswordType(
        schemes=[
            'pbkdf2_sha512',
        ],
    ))


    def is_authenticated(self):
        return bool(self.id)


    def is_active(self):
        return bool(self.id)


    def is_anonymous(self):
        return not bool(self.id)


    def get_id(self):
        return str(self.id)


class Retailer(db.Model):
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    version = db.Column(db.DateTime, nullable=False, default=datetime.now())
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    name = db.Column(db.String)
    fees_proportion = db.Column(db.Numeric)
    address = db.Column(db.String)
    zip = db.Column(db.String)
    city = db.Column(db.String)
    country = db.Column(db.String)
    contact_firstname = db.Column(db.String)
    contact_lastname = db.Column(db.String)


class ProductCost(db.Model):
    __tablename__ = 'product_cost'
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    version = db.Column(db.DateTime, nullable=False, default=datetime.now())
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    product_id = db.Column(db.Integer)
    value = db.Column(db.Numeric)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)


class RetailerProduct(db.Model):
    __tablename__ = 'retailer_product'
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    version = db.Column(db.DateTime, nullable=False, default=datetime.now())
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    retailer_id = db.Column(db.Integer, db.ForeignKey('retailer.id'))
    product_id = db.Column(db.Integer)
    order_date = db.Column(db.Date)
    sold_date = db.Column(db.Date)
    payment_date = db.Column(db.Date)

