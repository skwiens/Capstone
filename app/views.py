from flask import Flask, render_template, request, url_for, redirect, session, flash
from . import app
from .forms import VolunteerForm, RecordForm, UserForm
from .models import Record, Volunteer, User
from app import db
from functools import wraps

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add_volunteer', methods=['GET', 'POST'])
def add_volunteer():
    form = VolunteerForm(request.form)
    if request.method == 'POST' and form.validate():

        new_volunteer = Volunteer(
            name = form.name.data,
            email = form.email.data,
            role = form.role.data
        )

        db.session.add(new_volunteer)
        db.session.commit()

        flash('Volunteer ' + new_volunteer.name + ' added!', 'success')

        return redirect(url_for('index'))
    return render_template('volunteer_form.html', form=form)


@app.route('/volunteer/edit/<string:id>', methods=['GET', 'POST'])
def edit_volunteer(id):

    volunteer = Volunteer.query.get(id)
    form = VolunteerForm(request.form, obj=volunteer)

    if request.method == 'POST' and form.validate():
        form.populate_obj(volunteer)

        db.session.commit()

        flash('Information from ' + volunteer.name + ' Updated', 'success')

        return redirect(url_for('index'))
    else:
        return render_template('volunteer_form.html', form=form)


@app.route('/volunteers')
def volunteers():
    volunteers = Volunteer.query.all()

    if volunteers:
        return render_template('volunteers.html', volunteers=volunteers)
    else:
        msg = 'No Records Found'
        return render_template('volunteers.html', msg=msg)


@app.route('/edit_user', methods=['GET', 'POST'])
def edit_user():

    user = User.query.get(1)
    form = UserForm(request.form, obj=user)

    if request.method == 'POST' and form.validate():
        form.populate_obj(user)

        db.session.commit()

        flash('User login updated')

        return redirect(url_for('index'))
    else:
        return render_template('user.html', form=form)


@app.route('/add_user', methods=['GET', 'POST'])
def new_user():

    form = UserForm(request.form)

    if request.method == 'POST' and form.validate():
        new_user = User(
            username = form.username.data,
            password = form.password.data
        )

        db.session.add(new_user)
        db.session.commit()

        db.session.commit()

        flash('User login updated')

        return redirect(url_for('index'))
    else:
        return render_template('user.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user:
            if password_candidate == user.password:
                session['logged_in_user'] = True
                session['username'] = username
                # session['user'] = True

                flash('Your are now logged in as a volunteer', 'success')
                return redirect(url_for('index'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
        else:
            return render_template('login.html')
            error='Username not found'
            return render_template('login.html', error=error)
    return render_template('login.html')

# def is_logged_in(f):
#     @wraps(f)
#     def wrap(*args, **kwargs):
#         if 'logged_in' in session:
#             return f(*args, **kwargs)
#         else:
#             flash('Please log in to see this page', 'danger')
#             return redirect(url_for('login'))
#     return wrap

def user_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in_user' in session:
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


@app.route('/record/<string:id>')
def record(id):
    record = Record.query.get(id)

    return render_template('record.html', record=record)


@app.route('/add_record', methods=['GET', 'POST'])
@user_logged_in
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
