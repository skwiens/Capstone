from flask import Flask, render_template, request, url_for, redirect, session, flash
from config import DevConfig
from flask_sqlalchemy import SQLAlchemy
# from flask_wtf import FlaskForm
from wtforms import Form, StringField, TextAreaField, PasswordField, SelectField, validators
# from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired, Email, Length
from wtforms.fields.html5 import DateField
from passlib.hash import sha256_crypt
from functools import wraps
from flask_bcrypt import Bcrypt

app = Flask(__name__)

app.config.from_object(DevConfig)
app.config.from_object(DevConfig)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    records = db.relationship('Record', backref='user', lazy='dynamic')

    def __init__(self, name, username, email, password):
        self.name = name
        self.username = username
        self. email = email
        self.password = password

    def __repr__(self):
        return "<User '{}'>".format(self.username)

class Record(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    author = db.Column(db.Integer(), db.ForeignKey('user.id'))
    date = db.Column(db.DateTime(), unique=True)
    volunteers = db.Column(db.String(255))
    notes = db.Column(db.Text())
    shopping = db.Column(db.Text())

    def __init__(self, author, date, volunteers, notes, shopping):
        self.author = author
        self.date = date
        self.volunteers = volunteers
        self.notes = notes
        self.shopping = shopping

    def __repr__(self):
        return "<Record '{}'>".format(self.title)

@app.route('/')
def index():
    return render_template('index.html')

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.DataRequired(), validators.Email(), validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        new_user = User(
            name = form.name.data,
            username = form.username.data,
            email = form.email.data,
            password = bcrypt.generate_password_hash(str(form.password.data))
        )

        db.session.add(new_user)
        db.session.commit()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('index'))
    return render_template('register.html', form=form)

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

@app.route('/user/edit/<string:username>', methods=['GET', 'POST'])
@is_logged_in
def edit_user(username):
    if username != session['username']:
        flash('You are not authorized to change this information', 'danger')
    else:
        user = User.query.filter_by(username=username).first()
        form = RegisterForm(request.form)

        form.username.data = user.username
        form.email.data = user.email

        if request.method == 'POST' and form.validate():
            user.name = form.name.data,
            user.username = form.username.data,
            user.email = form.email.data,
            user.password = bcrypt.generate_password_hash(str(form.password.data))

            db.session.commit()

            flash('User Information Updated', 'success')

            return redirect(url_for('index'))
        else:
            return render_template('edit_user.html', form=form)

def volunteer_query():
    return User.query

class RecordForm(Form):
    # author = QuerySelectField(query_factory=volunteer_query, allow_blank=True, get_label='name')
    author = StringField('Name')
    date = DateField('Date', format='%Y-%m-%d')
    volunteers = StringField('Volunteers')
    notes = TextAreaField('Notes')
    shopping = TextAreaField('Shopping List')

@app.route('/add_record', methods=['GET', 'POST'])
@is_logged_in
def add_record():
    form = RecordForm(request.form)
    if request.method == 'POST' and form.validate():
        new_record = Record(
            author = form.author.data,
            date = form.date.data,
            volunteers = form.volunteers.data,
            notes = form.notes.data,
            shopping = form.shopping.data
        )

        db.session.add(new_record)
        db.session.commit()

        flash('Record for ' + new_record.date.strftime('%m/%d/%Y') + 'saved! Thank you for volunteering with us!', 'success')

        return redirect(url_for('index'))

    return render_template('add_record.html', form=form)

if __name__ == '__main__':
    app.run()
