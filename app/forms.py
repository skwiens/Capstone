from flask_wtf import Form
from wtforms import StringField, SelectField, DateField, IntegerField, TextAreaField
# from wtforms.validators import DataRequired, Email

class VolunteerForm(Form):
    # name = StringField('Name', [validators.Length(min=1, max=50)])
    # email = StringField('Email', [validators.DataRequired(), validators.Email(), validators.Length(min=6, max=50)])
    # role = StringField('Role')
    role = SelectField('Role', choices = [('open-hours', 'open-hours'), ('shopper','shoppers'), ('both', 'both')] )


class RecordForm(Form):
    # author = QuerySelectField(query_factory=volunteer_query, allow_blank=True, get_label='name')
    author = StringField('Name')
    # author = QuerySelectField(query_factory=volunteer_query, allow_blank=True)
    date = DateField('Date', format='%Y-%m-%d')
    volunteers = StringField('Volunteers')
    customers = IntegerField('Number of Customers')
    notes = TextAreaField('Notes')
    shopping = TextAreaField('Shopping List')
