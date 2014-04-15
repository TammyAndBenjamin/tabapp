from flask_wtf import Form
from wtforms import FormField, TextField, FieldList, IntegerField
from wtforms.validators import DataRequired


class ItemLine(Form):
    variant_id = IntegerField('Produit')
    quantity = IntegerField('Quantité')


class OrderForm(Form):
    customer_firstname = TextField('Prénom', validators=[DataRequired()])
    customer_lastname = TextField('Nom', validators=[DataRequired()])
    customer_email = TextField('Email', validators=[DataRequired()])
    item_lines = FieldList(FormField(ItemLine))
