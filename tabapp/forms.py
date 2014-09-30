from flask_wtf import Form
from wtforms import FormField, TextField, FieldList, DecimalField
from wtforms.validators import DataRequired, NumberRange


class RetailerForm(Form):
    name = TextField('Name', validators=[DataRequired()])
    fees_proportion = DecimalField('Fees', validators=[DataRequired(), NumberRange(0, 100)])
    address = TextField('Address')
    zip = TextField('Zip', validators=[DataRequired()])
    city = TextField('City')
    country = TextField('Country')
    contact_firstname = TextField('Contact firstname', validators=[DataRequired()])
    contact_lastname = TextField('Contact lastname', validators=[DataRequired()])
