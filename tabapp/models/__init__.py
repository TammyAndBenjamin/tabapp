# -*- coding: utf-8 -*-

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
            crit = mzero.class_.enabled is True
            return self.enable_assertions(False).filter(crit)
        else:
            return self


#Model.query_class = LimitingQuery
db = SQLAlchemy(session_options={'query_cls': LimitingQuery})


from tabapp.models.contact import Contact
from tabapp.models.product_cost import ProductCost
from tabapp.models.product import Product
from tabapp.models.retailer_product import RetailerProduct
from tabapp.models.invoice_item import InvoiceItem
from tabapp.models.invoice import Invoice
from tabapp.models.retailer import Retailer
from tabapp.models.delivery_slip_line import DeliverySlipLine
from tabapp.models.delivery_slip import DeliverySlip
from tabapp.models.url import Url, UrlClick
from tabapp.models.lead import Lead
from tabapp.models.order import ProductOrder
