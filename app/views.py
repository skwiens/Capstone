from flask import Flask, render_template, request, url_for, redirect, session, flash
from . import app
from .forms import VolunteerForm, OpenhourForm, UserForm, EmailForm
from .models import Volunteer, Openhour, User, Email
from app import db
from functools import wraps
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from requests_oauthlib import OAuth2Session
from .config import Auth

import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery


#### HELP!  NEED THIS TO BE NOT A FILE! #####
CLIENT_SECRETS_FILE = 'client_secret.json'
# CLIENT_SECRETS_FILE = os.environ['CLIENT_SECRETS_FILE']
SCOPES = ['https://www.googleapis.com/auth/gmail.compose']
API_SERVICE_NAME = 'gmail'
API_VERSION = 'v1'

import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

def user_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in_user' in session:
            return f(*args, **kwargs)
        else:
            flash('Please log in to see this page', 'danger')
            return redirect(url_for('user_login'))
    return wrap

def admin_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user' in session and session['user']=='admin':
            return f(*args, **kwargs)
        else:
            flash('You must have admin privileges to complete this action', 'danger')
            return redirect(url_for('index'))
    return wrap

@app.route('/admin_login')
def admin_login():
    if 'credentials' not in session:
        return redirect('authorize')

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
      **session['credentials'])

    service = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)

    if service:
        user_profile = service.users().getProfile(userId='me').execute()
        emailAddress = user_profile['emailAddress']
        if user_profile['emailAddress'] == 'xana.wines.ada@gmail.com':
            session['user'] = 'admin'
            flash('You are now logged in as an administrator', 'success')
            # redirect(url_for('index'))
        else:
            flash('You do not have admin privileges, please contact Bethany Food Bank if you have any questions', 'danger')
            redirect(url_for('clear'))
    else:
        flash('Sorry! Something went wrong. Please try again in a few moments', 'danger')


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


    return redirect(url_for('admin_login'))

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
    return('Credentials successfully revoked.')
  else:
    return('An error occurred.')

# @app.route('/clear')
# def clear_credentials():
#   if 'credentials' in session:
#     del session['credentials']
#   if 'user' in session:
#     del session['user']
#   return redirect(url_for('index'))


def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}



# from OpenSSL import SSL
# context = SSL.Context(SSL.SSLv23_METHOD)
# context.use_privatekey_file('localhost.key')
# context.use_certificate_file('localhost.crt')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_volunteer', methods=['GET', 'POST'])
# @admin_logged_in
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
# @admin_logged_in
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
# @admin_logged_in
def volunteers():
    volunteers = Volunteer.query.all()

    if volunteers:
        return render_template('volunteers.html', volunteers=volunteers)
    else:
        msg = 'No Records Found'
        return render_template('volunteers.html', msg=msg)


@app.route('/edit_user', methods=['GET', 'POST'])
# @admin_logged_in
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
# @admin_logged_in
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
                session['user'] = 'volunteer'
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

@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('index'))


@app.route('/openhour/<string:id>')
# @admin_logged_in
def openhour(id):
    openhour = Openhour.query.get(id)

    return render_template('record.html', openhour=openhour)


@app.route('/add_openhour', methods=['GET', 'POST'])
# @user_logged_in
def add_openhour():
    form = OpenhourForm(request.form)

    volunteer_list = [(volunteer.id, volunteer.name) for volunteer in Volunteer.query.all()]
    form.volunteer.choices = volunteer_list

    if request.method == 'POST' and form.validate():
        new_openhour = Openhour(
            # author = form.author.data,
            date = form.date.data,
            # volunteer = Volunteer.query.get(form.volunteer.data)
            # customers = form.customers.data,
            # notes = form.notes.data,
            # shopping = form.shopping.data
        )

        db.session.add(new_openhour)
        new_openhour.volunteer.append(Volunteer.query.get(form.volunteer.data))
        db.session.commit()

        flash('Record for ' + new_openhour.date.strftime('%m/%d/%Y') + 'saved! Thank you for volunteering with us!', 'success')

        return redirect(url_for('index'))

    return render_template('add_openhour.html', form=form)


@app.route('/openhours')
# @admin_logged_in
def openhours():
    openhours = Openhour.query.all()

    if openhours:
        return render_template('records.html', openhours=openhours)
    else:
        msg = 'No Records Found'
        return render_template('records.html', msg=msg)

@app.route('/add_email', methods=['GET', 'POST'])
# @admin_logged_in
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

# @app.route('/send_email')
# def send_message():
#     main()


if __name__ == '__main__':
    app.run()
