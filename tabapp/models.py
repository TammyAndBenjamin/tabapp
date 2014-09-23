# -*- coding: utf-8 -*-


from tabapp import db


class Login(db.Model):
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key = True)
    username = db.Column(db.String, index = True, unique = True)
    password = db.Column(db.String)

    def is_authenticated(self):
        return bool(self.id)


    def is_active(self):
        return bool(self.id)


    def is_anonymous(self):
        return not bool(self.id)


    def get_id(self):
        return str(self.id)


class Retailer(db.Model):
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key = True)
    name = db.Column(db.String)
    address = db.Column(db.String)
    zip = db.Column(db.String)
    city = db.Column(db.String)


class ProductCost(db.Model):
    __tablename__ = 'product_cost'
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key = True)
    product_id = db.Column(db.Integer)
    value = db.Column(db.Numeric)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)


class RetailerProduct(db.Model):
    __tablename__ = 'retailer_product'
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key = True)
    retailer_id = db.Column(db.Integer, index = True)
    product_id = db.Column(db.Integer)
    order_date = db.Column(db.Date)
    sold_date = db.Column(db.Date)
    payment_date = db.Column(db.Date)

