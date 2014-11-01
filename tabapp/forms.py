from flask_wtf import Form
from wtforms import TextField
from wtforms.fields.html5 import DecimalField
from wtforms.validators import DataRequired, NumberRange
from flask.ext.babel import lazy_gettext


class RetailerForm(Form):
    name = TextField(lazy_gettext('Name'), validators=[DataRequired()])
    code = TextField(lazy_gettext('Code'), validators=[DataRequired()])
    fees_proportion = DecimalField(lazy_gettext('Fees'), validators=[DataRequired(), NumberRange(0, 100)])
    address = TextField(lazy_gettext('Address'))
    zip = TextField(lazy_gettext('Zip'))
    city = TextField(lazy_gettext('City'))
    country = TextField(lazy_gettext('Country'))
    contact_firstname = TextField(lazy_gettext('Contact firstname'), validators=[DataRequired()])
    contact_lastname = TextField(lazy_gettext('Contact lastname'), validators=[DataRequired()])
