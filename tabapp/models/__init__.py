# -*- coding: utf-8 -*-

from tabapp import app
from flask.ext.sqlalchemy import SQLAlchemy, Model, BaseQuery


class LimitingQuery(BaseQuery):
    def get(self, ident):
        # override get() so that the flag is always checked in the 
        # DB as opposed to pulling from the identity map. - this is optional.
        return BaseQuery.get(self.populate_existing(), ident)

    def __iter__(self):
        return BaseQuery.__iter__(self.private())

    def from_self(self, *ent):
        # override from_self() to automatically apply
        # the criterion too. This works with count() and
        # others.
        return BaseQuery.from_self(self.private(), *ent)

    def private(self):
        mzero = self._mapper_zero()
        if mzero is not None:
            crit = mzero.class_.enabled == True
            return self.enable_assertions(False).filter(crit)
        else:
            return self


Model.query_class = LimitingQuery
db = SQLAlchemy(app, session_options={'query_cls': LimitingQuery})


from .login import Login
from .product import Product
from .product_cost import ProductCost
from .retailer import Retailer
from .retailer_product import RetailerProduct
