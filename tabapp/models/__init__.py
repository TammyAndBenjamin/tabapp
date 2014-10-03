# -*- coding: utf-8 -*-

from tabapp import app
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm.query import Query


class LimitingQuery(Query):
    def get(self, ident):
        # override get() so that the flag is always checked in the 
        # DB as opposed to pulling from the identity map. - this is optional.
        return Query.get(self.populate_existing(), ident)

    def __iter__(self):
        return Query.__iter__(self.private())

    def from_self(self, *ent):
        # override from_self() to automatically apply
        # the criterion too. This works with count() and
        # others.
        return Query.from_self(self.private(), *ent)

    def private(self):
        mzero = self._mapper_zero()
        if mzero is not None:
            crit = mzero.class_.enabled == True

            return self.enable_assertions(False).filter(crit)
        else:
            return self

db = SQLAlchemy(app, session_options={'query_cls': LimitingQuery})

__all__ = ['login', 'product_cost', 'retailer', 'retailer_product']
