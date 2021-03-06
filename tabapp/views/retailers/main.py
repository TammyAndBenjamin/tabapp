# -*- coding: utf-8 -*-

from flask import (
    Blueprint,
    request,
    render_template,
    redirect, url_for, flash, jsonify,
    abort, g
)
from flask_babel import gettext as _
from flask_principal import Permission, ItemNeed, RoleNeed
from tabapp.extensions.security import permisssion_required
from tabapp.models import (
    db, Invoice, InvoiceItem, Retailer,
    RetailerProduct, Contact
)
from tabapp.forms import RetailerForm, ContactForm
from tabapp.views.retailers import tab_counts
import tabapp.utils


retailers_bp = Blueprint('retailers_bp', __name__, subdomain='backyard')


@retailers_bp.route('/')
@permisssion_required(['normal', 'retailer'])
def index():
    permisssion = Permission(RoleNeed('normal'))
    retailers = Retailer.query.all()
    for retailer in retailers[:]:
        need = ItemNeed('access', 'retailer', retailer.id)
        if not permisssion.union(Permission(need)).can():
            retailers.remove(retailer)
    context = {
        'retailers': retailers,
    }
    return render_template('retailers/index.html', **context)


@retailers_bp.route('/<int:retailer_id>/', methods=['GET'])
@permisssion_required(['normal', 'retailer'])
def retailer(retailer_id):
    permisssion = Permission(RoleNeed('normal'))
    need = ItemNeed('access', 'retailer', retailer_id)
    if not permisssion.union(Permission(need)).can():
        return abort(403)
    retailer = Retailer.query.get(retailer_id)
    if not retailer:
        return abort(404)
    context = {
        'retailer': retailer,
        'tab_counts': tab_counts(retailer),
    }
    return render_template('retailers/retailer.html', **context)


@retailers_bp.route('/new')
@permisssion_required(['normal'])
def new_retailer():
    form = RetailerForm()
    context = {
        'retailer_id': None,
        'form': form,
    }
    return render_template('retailers/form.html', **context)


@retailers_bp.route('/', defaults={'retailer_id': None}, methods=['POST'])
@retailers_bp.route('/<int:retailer_id>/', methods=['POST'])
@retailers_bp.route('/<int:retailer_id>/edit', methods=['GET', 'POST'])
@permisssion_required(['normal'])
def edit_retailer(retailer_id):
    form = None
    if request.method == 'POST':
        form = RetailerForm(request.form)
        if form.validate():
            retailer = Retailer.query.get(retailer_id)\
                if retailer_id else Retailer()
            form.populate_obj(retailer)
            retailer.fees_proportion = form.fees_proportion.data / 100
            if not retailer.id:
                db.session.add(retailer)
            db.session.commit()
            flash(_('Retailer updated.'), 'success')
            kwargs = {
                'retailer_id': retailer.id,
            }
            return redirect(url_for('retailers_bp.retailer', **kwargs))
    retailer = Retailer.query.get(retailer_id) if retailer_id else Retailer()
    form = RetailerForm(obj=retailer) if not form else form
    form.fees_proportion.data = form.fees_proportion.data * 100\
        if form.fees_proportion.data else 0
    context = {
        'retailer_id': retailer.id,
        'form': form,
    }
    return render_template('retailers/form.html', **context)


@retailers_bp.route('/<int:retailer_id>/', methods=['DELETE'])
@retailers_bp.route('/<int:retailer_id>/delete', methods=['POST'])
@permisssion_required(['normal'])
def delete_retailer(retailer_id):
    retailer = Retailer.query.get(retailer_id)
    if not retailer:
        return abort(404)
    db.session.delete(retailer)
    db.session.commit()
    if tabapp.utils.request_wants_json():
        return jsonify(success=_('Retailer deleted.'))
    flash(_('Retailer deleted.'), 'success')
    return redirect(url_for('retailers_bp.index'))


@retailers_bp.route('/<int:retailer_id>/sold/')
@permisssion_required(['normal'])
def sold(retailer_id):
    retailer = Retailer.query.get(retailer_id)
    context = {
        'retailer': retailer,
        'stocks': retailer.stocks.filter(
            RetailerProduct.sold_date.isnot(None),
            RetailerProduct.invoice_item_id.is_(None)
        ),
        'tab_counts': tab_counts(retailer),
    }
    return render_template('retailers/sold.html', **context)


@retailers_bp.route('/<int:retailer_id>/invoices/')
@permisssion_required(['normal'])
def invoices(retailer_id):
    retailer = Retailer.query.get(retailer_id)
    context = {
        'retailer': retailer,
        'invoices': retailer.invoices,
        'tab_counts': tab_counts(retailer),
    }
    return render_template('retailers/invoices.html', **context)


@retailers_bp.route('/<int:retailer_id>/invoices/<int:invoice_id>/')
@permisssion_required(['normal'])
def invoice(retailer_id, invoice_id):
    retailer = Retailer.query.get(retailer_id)
    invoice = Invoice.query.get(invoice_id)
    context = {
        'retailer': retailer,
        'invoice': invoice,
    }
    return render_template('retailers/invoice.html', **context)


@retailers_bp.route('/<int:retailer_id>/invoices/', methods=['POST'])
@permisssion_required(['normal'])
def make_invoice(retailer_id):
    retailer = Retailer.query.get(retailer_id)
    retailer_product_ids = request.form.getlist('retailer_product_ids[]')
    if not retailer:
        return abort(404)
    if not retailer_product_ids:
        return abort(400)
    invoice = Invoice()
    db.session.add(invoice)
    invoice.retailer_id = retailer.id
    for retailer_product_id in retailer_product_ids:
        retailer_product = RetailerProduct.query.get(retailer_product_id)
        excl_tax_unit_price = retailer_product.product.unit_price * (1 - retailer.fees_proportion)
        incl_tax_unit_price = excl_tax_unit_price * g.config['APP_VAT']
        tax = incl_tax_unit_price - excl_tax_unit_price

        invoice_item = invoice.items.filter(
            InvoiceItem.orders.any(
                RetailerProduct.product_id == retailer_product.product_id)).first()
        if not invoice_item:
            invoice_item = InvoiceItem()
            invoice_item.title = retailer_product.product.title
            invoice_item.unit_price = excl_tax_unit_price
        invoice_item.orders.append(retailer_product)

        invoice_item.quantity = invoice_item.orders.count()
        invoice_item.excl_tax_price = excl_tax_unit_price * invoice_item.quantity
        invoice_item.tax_price = tax * invoice_item.quantity
        invoice_item.incl_tax_price = invoice_item.excl_tax_price + invoice_item.tax_price

        invoice.items.append(invoice_item)
    db.session.commit()
    if tabapp.utils.request_wants_json():
        return jsonify(success=_('Product pay.'), tab_counts=tab_counts(retailer))
    flash(_('Product pay.'), 'success')
    kwargs = {
        'retailer_id': retailer.id,
    }
    return redirect(url_for('retailers_bp.sold', **kwargs))


@retailers_bp.route('/<int:retailer_id>/contacts/')
@permisssion_required(['normal', 'retailer'])
def contacts(retailer_id):
    permisssion = Permission(RoleNeed('normal'))
    need = ItemNeed('access', 'retailer', retailer_id)
    if not permisssion.union(Permission(need)).can():
        return abort(403)
    retailer = Retailer.query.get(retailer_id)
    context = {
        'retailer': retailer,
        'contacts': retailer.contacts,
        'tab_counts': tab_counts(retailer),
    }
    return render_template('retailers/contacts.html', **context)


@retailers_bp.route('/<int:retailer_id>/contacts/new', defaults={'contact_id': None}, methods=['GET', 'POST'])
@retailers_bp.route('/<int:retailer_id>/contacts/<int:contact_id>/', methods=['GET', 'POST'])
@permisssion_required(['normal', 'retailer'])
def contact(retailer_id, contact_id):
    permisssion = Permission(RoleNeed('normal'))
    need = ItemNeed('access', 'retailer', retailer_id)
    if not permisssion.union(Permission(need)).can():
        return abort(403)
    retailer = Retailer.query.get(retailer_id)
    contact = Contact.query.get(contact_id) if contact_id else Contact()
    contact_form = ContactForm(obj=contact)
    del contact_form.roles
    if contact_form.validate_on_submit():
        contact_form.populate_obj(contact)
        contact.phone = contact_form.phone.data
        if not contact.id:
            retailer.contacts.append(contact)
        db.session.commit()
        flash(_('User updated.'), 'success')
        kwargs = {
            'retailer_id': retailer.id,
            'contact_id': contact.id,
        }
        return redirect(url_for('retailers_bp.contact', **kwargs))
    context = {
        'user_id': contact.id,
        'retailer': retailer,
        'tab_counts': tab_counts(retailer),
        'contact': contact,
        'contact_form': contact_form,
    }
    return render_template('retailers/contact.html', **context)
