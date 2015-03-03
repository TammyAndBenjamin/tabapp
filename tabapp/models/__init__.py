# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy(session_options={'expire_on_commit': False})

from tabapp.models.contact import Locale, Contact
from tabapp.models.role import Role
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
