from flask_wtf import Form
from wtforms import TextField, PasswordField, SelectMultipleField
from wtforms import widgets
from wtforms.fields.html5 import DecimalField
from wtforms.validators import DataRequired, NumberRange, Email
from flask.ext.babel import lazy_gettext


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


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


class ContactForm(Form):
    firstname = TextField(lazy_gettext('Firstname'), validators=[DataRequired()])
    lastname = TextField(lazy_gettext('Lastname'), validators=[DataRequired()])
    email = TextField(lazy_gettext('Email'), validators=[DataRequired(), Email()])
    phone = TextField(lazy_gettext('Phone'))
    roles = MultiCheckboxField(lazy_gettext('Roles'), choices=[], coerce=int)


class CredentialsForm(Form):
    username = TextField(lazy_gettext('Username'), validators=[DataRequired()])
    password = PasswordField(lazy_gettext('Password'), validators=[DataRequired()])
