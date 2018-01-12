from flask_wtf import Form
# from flask_wtf import FlaskForm
from wtforms import Form, StringField, TextAreaField, IntegerField, SelectField, validators
# from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired, Email, Length
from wtforms.fields.html5 import DateField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Email

from .models import Volunteer

# def volunteer_query():
#     volunteers = Volunteer.query.all()
#     volunteer_list = [(volunteer.id, volunteer.name) for volunteer in volunteers]
#
#     return volunteer_list

class VolunteerForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    email = StringField('Email', [validators.DataRequired(), validators.Email(), validators.Length(min=6, max=50)])
    role = StringField('Role')
    role = SelectField('Role', choices = [('open-hours', 'open-hours'), ('shopper','shoppers'), ('both', 'both')] )

class OpenhourForm(Form):
    # choices = volunteer_query()
    # choices=[('none', 'none')]
    # author = SelectField('Author', choices=choices)
    # author = StringField('Name')
    # author = QuerySelectField(query_factory=volunteer_query, allow_blank=True)
    date = DateField('Date', format='%Y-%m-%d')
    volunteer = SelectField('Volunteer', coerce=int)
    # customers = IntegerField('Number of Customers')
    # notes = TextAreaField('Notes')
    # shopping = TextAreaField('Shopping List')


class UserForm(Form):
    username = StringField('Username', [validators.Length(min=1, max=50)])
    password = StringField('Password', [validators.DataRequired()])

class EmailForm(Form):
    send_date = DateField('Send Date', format='%Y-%m-%d')
    recipients = StringField('To: ')
    subject = StringField('Subject: ')
    message = TextAreaField('Body')
