# -*- coding: utf-8 -*-

import tabapp.utils
from datetime import datetime
from tabapp.models import db


class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, db.Sequence('core_seq_general'), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    version = db.Column(db.DateTime, nullable=False, default=datetime.now())
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    title = db.Column(db.String, nullable=False)
    quantity = db.Column(db.Integer)
    unit_price = db.Column(db.Numeric)
    image = db.Column(db.String)
    remote_id = db.Column(db.Integer, nullable=False)
    last_sync = db.Column(db.DateTime, nullable=False, default=datetime.now())

    @staticmethod
    def sync_from_remote():
        fields = [
            'id',
            'title',
            'updated_at',
            'images',
            'variants',
        ]
        resource = 'products'
        params = '?page={{page}}&fields={fields}&published_status=published'.format(**{
            'fields': ','.join(fields),
        })
        rows = tabapp.utils.list_from_resource(resource, params)
        for row in rows:
            product = Product.query.filter(Product.remote_id == row.get('id')).first()
            if product and product.last_sync.isoformat() >= row.get('updated_at'):
                continue
            if not product:
                product = Product()
                product.remote_id = row.get('id')
            product.title = row.get('title')
            product.quantity = row.get('variants')[0].get('inventory_quantity')
            product.unit_price = row.get('variants')[0].get('price')
            product.image = row.get('images')[0].get('src')
            product.last_sync = datetime.now()
            if not product.id:
                db.session.add(product)
        db.session.commit()
