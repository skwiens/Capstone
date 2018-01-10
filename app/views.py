from flask import Flask, render_template, request, url_for, redirect, session, flash
from . import app
from .forms import VolunteerForm, RecordForm, UserForm, EmailForm
from .models import Record, Volunteer, User, Email
from app import db
from functools import wraps
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from requests_oauthlib import OAuth2Session
from .config import Auth

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

CLIENT_SECRETS_FILE = 'client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/gmail.compose']
API_SERVICE_NAME = 'gmail'
API_VERSION = 'v1'

import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

@app.route('/admin_login')
def test_api_request():
    if 'credentials' not in session:
        return redirect('authorize')

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
      **session['credentials'])

    service = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)

    if service:
        print('Successfully accessed gmail')
        if 'user' in session:
            print(session['user'])
        else:
            print('no user in session')

    return redirect(url_for('index'))


@app.route('/authorize')
def authorize():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES)

    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')

    session['state'] = state

    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    state = session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)
    session['user'] = 'admin'


    return redirect(url_for('test_api_request'))


@app.route('/revoke')
def revoke():
  if 'credentials' not in session:
    return ('You need to <a href="/authorize">authorize</a> before ' +
            'testing the code to revoke credentials.')

  credentials = google.oauth2.credentials.Credentials(**session['credentials'])

  revoke = requests.post('https://accounts.google.com/o/oauth2/revoke',
      params={'token': credentials.token},
      headers = {'content-type': 'application/x-www-form-urlencoded'})

  status_code = getattr(revoke, 'status_code')
  if status_code == 200:
    return('Credentials successfully revoked.' + print_index_table())
  else:
    return('An error occurred.' + print_index_table())

@app.route('/clear')
def clear_credentials():
  if 'credentials' in session:
    del session['credentials']
  if 'user' in session:
    del session['user']
  return ('Credentials have been cleared.<br><br>')


def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}



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

@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
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
                return render_template('user_login.html', error=error)
        else:
            return render_template('user_login.html')
            error='Username not found'
            return render_template('user_login.html', error=error)
    return render_template('user_login.html')



def user_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in_user' in session:
            return f(*args, **kwargs)
        else:
            flash('Please log in to see this page', 'danger')
            return redirect(url_for('user_login'))
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

@app.route('/add_email', methods=['GET', 'POST'])
def add_email():
    form = EmailForm(request.form)
    if request.method == 'POST' and form.validate():
        new_email = Email(
            send_date = form.send_date.data,
            recipients = form.recipients.data,
            subject = form.subject.data,
            message = form.message.data
        )

        db.session.add(new_email)
        db.session.commit()

        flash('Email created but not sent', 'success')

        return redirect(url_for('index'))

    return render_template('new_email.html', form=form)

@app.route('/send_email')
def send_message():
    main()


if __name__ == '__main__':
    app.run()
