from flask import Flask, render_template, request, url_for, redirect, session, flash
from . import app
from .forms import VolunteerForm, RecordForm
from .models import Record, Volunteer

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_volunteer', methods=['GET', 'POST'])
def add_volunteer():
    form = VolunteerForm(request.form)
    if request.method == 'POST' and form.validate():
        print(form.role.data)

        new_volunteer = Volunteer(
            name = form.name.data,
            email = form.email.data,
            role = form.role.data
        )

        db.session.add(new_volunteer)
        db.session.commit()

        flash('Volunteer ' + new_volunteer.role + ' added!', 'success')

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
