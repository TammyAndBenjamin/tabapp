# -*- coding: utf-8 -*-

from tabapp.models import Invoice, RetailerProduct, DeliverySlip


def tab_counts(retailer):
    counts = {
        'delivery_slips': DeliverySlip.query.filter(
            DeliverySlip.retailer_id == retailer.id
        ).count(),
        'stocks': RetailerProduct.query.filter(
            RetailerProduct.retailer_id == retailer.id,
            RetailerProduct.sold_date.is_(None)
        ).count(),
        'sold': RetailerProduct.query.filter(
            RetailerProduct.retailer_id == retailer.id,
            RetailerProduct.sold_date.isnot(None),
            RetailerProduct.invoice_item_id.is_(None)
        ).count(),
        'invoices': Invoice.query.filter(
            Invoice.retailer_id == retailer.id
        ).count(),
        'contacts': len(retailer.contacts),
    }
    return counts
