from flask import Flask, render_template, request, url_for, redirect, session, flash
from config import DevConfig
from flask_sqlalchemy import SQLAlchemy
# from flask_wtf import FlaskForm
from wtforms import Form, StringField, TextAreaField, IntegerField, SelectField, validators
# from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired, Email, Length
from wtforms.fields.html5 import DateField
from wtforms_sqlalchemy.fields import QuerySelectField
from passlib.hash import sha256_crypt
from functools import wraps
from flask_bcrypt import Bcrypt


app = Flask(__name__)

app.config.from_object(DevConfig)
app.config.from_object(DevConfig)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class Volunteer(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))
    position = db.Column(db.String(50))
    email = db.Column(db.String(255), unique=True, nullable=False)
    # records = db.relationship('Record', backref='volunteer', lazy='dynamic')

    def __init__(self, name, email, position):
        self.name = name
        self.email = email
        self.position = position

    def __repr__(self):
        return "<Volunteer '{}'>".format(self.name)

class Record(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    # author = db.Column(db.Integer(), db.ForeignKey('volunteer.id'))
    author = db.Column(db.String(255))
    date = db.Column(db.DateTime())
    volunteers = db.Column(db.String(255))
    customers = db.Column(db.Integer())
    notes = db.Column(db.Text())
    shopping = db.Column(db.Text())

    def __init__(self, author, date, volunteers, customers, notes, shopping):
        self.author = author
        self.date = date
        self.volunteers = volunteers
        self.customers = customers
        self.notes = notes
        self.shopping = shopping

    def __repr__(self):
        return "<Record '{}'>".format(self.title)

@app.route('/')
def index():
    return render_template('index.html')

class VolunteerForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    email = StringField('Email', [validators.DataRequired(), validators.Email(), validators.Length(min=6, max=50)])
    # role = StringField('Role')
    position = SelectField('Role', choices = [('open-hours', 'open-hours'), ('shopper','shoppers'), ('both', 'both')] )

@app.route('/add_volunteer', methods=['GET', 'POST'])
def add_volunteer():
    form = VolunteerForm(request.form)
    if request.method == 'POST' and form.validate():
        print(form.position.data)

        new_volunteer = Volunteer(
            name = form.name.data,
            email = form.email.data,
            position = form.position.data
        )

        db.session.add(new_volunteer)
        db.session.commit()

        flash('Volunteer ' + new_volunteer.position + ' added!', 'success')

        return redirect(url_for('index'))
    return render_template('volunteer_form.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user:
            if bcrypt.check_password_hash(user.password, password_candidate):
                session['logged_in'] = True
                session['username'] = username

                flash('Your are now logged in', 'success')
                return redirect(url_for('index'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
        else:
            error='Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Please log in to see this page', 'danger')
            return redirect(url_for('login'))
    return wrap

@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('index'))

# @app.route('/volunteer/edit/<string:id>', methods=['GET', 'POST'])
# # @is_logged_in
# def edit_volunteer(id):
#
#     volunteer = Volunteer.query.get(id)
#     form = VolunteerForm(request.form)
#
#     form.name.data = volunteer.name
#     form.email.data = volunteer.email
#     form.role.data = volunteer.role
#
#     if request.method == 'POST' and form.validate():
#         volunteer.name = form.name.data,
#         volunteer.email = form.volunteer.data,
#
#         db.session.commit()
#
#         flash('Information from ' + volunteer.name + ' Updated', 'success')
#
#         return redirect(url_for('index'))
#     else:
#         return render_template('edit_volunteer.html', form=form)


@app.route('/record/<string:id>')
def record(id):
    record = Record.query.get(id)

    return render_template('record.html', record=record)


def volunteer_query():
    return Volunteer.query

class RecordForm(Form):
    # author = QuerySelectField(query_factory=volunteer_query, allow_blank=True, get_label='name')
    author = StringField('Name')
    # author = QuerySelectField(query_factory=volunteer_query, allow_blank=True)
    date = DateField('Date', format='%Y-%m-%d')
    volunteers = StringField('Volunteers')
    customers = IntegerField('Number of Customers')
    notes = TextAreaField('Notes')
    shopping = TextAreaField('Shopping List')

@app.route('/add_record', methods=['GET', 'POST'])
# @is_logged_in
def add_record():
    form = RecordForm(request.form)
    if request.method == 'POST' and form.validate():
        new_record = Record(
            author = form.author.data,
            date = form.date.data,
            volunteers = form.volunteers.data,
            customers = form.customers.data,
            notes = form.notes.data,
            shopping = form.shopping.data
        )

        db.session.add(new_record)
        db.session.commit()

        flash('Record for ' + new_record.date.strftime('%m/%d/%Y') + 'saved! Thank you for volunteering with us!', 'success')

        return redirect(url_for('index'))

    return render_template('add_record.html', form=form)

@app.route('/records')
def records():
    records = Record.query.all()

    if records:
        return render_template('records.html', records=records)
    else:
        msg = 'No Records Found'
        return render_template('records.html', msg=msg)


if __name__ == '__main__':
    app.run()
