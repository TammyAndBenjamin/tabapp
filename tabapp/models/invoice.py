# -*- coding: utf-8 -*-

from datetime import date
from sqlalchemy.sql.expression import func
from sqlalchemy.orm import relationship, backref
from sqlalchemy_utils import aggregated
from tabapp.models import db, InvoiceItem
import calendar
import sqlalchemy


def generate_no(context):
    today = date.today()
    month_range = calendar.monthrange(today.year, today.month)
    first_day = date(today.year, today.month, 1)
    last_day = date(today.year, today.month, month_range[1])
    idx = Invoice.query.filter(Invoice.issue_date >= first_day,
        Invoice.issue_date <= last_day).count()
    return 'FC{}{:02d}{:03d}'.format(today.year, today.month, idx + 1)


class Invoice(db.Model):
    __tablename__ = 'invoice'
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=func.now())
    version = db.Column(db.DateTime, nullable=False, default=func.now(), onupdate=func.now())
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    retailer_id = db.Column(db.Integer, db.ForeignKey('retailer.id'))
    retailer = relationship('Retailer', backref=backref('invoices', lazy='dynamic'))
    issue_date = db.Column(db.Date, nullable=False, default=date.today)
    no = db.Column(db.String, nullable=False, default=generate_no)

    @aggregated('items', db.Column(db.Numeric))
    def excl_tax_price(self):
        return sqlalchemy.func.sum(InvoiceItem.excl_tax_price)

    @aggregated('items', db.Column(db.Numeric))
    def tax_price(self):
        return sqlalchemy.func.sum(InvoiceItem.tax_price)

    @aggregated('items', db.Column(db.Numeric))
    def incl_tax_price(self):
        return sqlalchemy.func.sum(InvoiceItem.incl_tax_price)
