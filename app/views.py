from flask import Flask, render_template, request, url_for, redirect, session, flash
from . import app
from .forms import VolunteerForm, RecordForm, UserForm, EmailForm
from .models import Record, Volunteer, User, Email
from app import db
from functools import wraps
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from requests_oauthlib import OAuth2Session
from .config import Auth

import httplib2
import os
import oauth2client
from oauth2client import client, tools
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apiclient import errors, discovery
import mimetypes
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase

SCOPES = 'https://www.googleapis.com/auth/gmail.compose'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Bethany Food Bank'

def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-email-send.json')
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def SendMessage(sender, to, subject, msgHtml, msgPlain, attachmentFile=None):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    if attachmentFile:
        message1 = createMessageWithAttachment(sender, to, subject, msgHtml, msgPlain, attachmentFile)
    else:
        message1 = CreateMessageHtml(sender, to, subject, msgHtml, msgPlain)
    result = SendMessageInternal(service, "me", message1)
    return result

def SendMessageInternal(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)
        return "Error"
    return "OK"

def CreateMessageHtml(sender, to, subject, msgHtml, msgPlain):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to
    msg.attach(MIMEText(msgPlain, 'plain'))
    msg.attach(MIMEText(msgHtml, 'html'))
    return {'raw': base64.urlsafe_b64encode(msg.as_string())}

def main():
    to = "to@address.com"
    sender = "from@address.com"
    subject = "subject"
    msgHtml = "Hi<br/>Html Email"
    msgPlain = "Hi\nPlain Email"
    SendMessage(sender, to, subject, msgHtml, msgPlain)
    # Send message with attachment:
    SendMessage(sender, to, subject, msgHtml, msgPlain, '/path/to/file.pdf')

@app.route('/')
def index():
    main()
    return print('did this work?')



######################################################
#
# import google.oauth2.credentials
# import google_auth_oauthlib.flow
# import googleapiclient.discovery
#
# CLIENT_SECRETS_FILE = 'client_secret.json'
# SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
# API_SERVICE_NAME = 'drive'
# API_VERSION = 'v2'
#
# @app.route('/')
# def index():
#     return print_index_table()
#
#
# @app.route('/test')
# def test_api_request():
#     if 'credentials' not in session:
#         return redirect('authorize')
#
#     # Load credentials from the session.
#     credentials = google.oauth2.credentials.Credentials(
#       **session['credentials'])
#
#     drive = googleapiclient.discovery.build(
#       API_SERVICE_NAME, API_VERSION, credentials=credentials)
#
#     files = drive.files().list().execute()
#
#     session['credentials'] = credentials_to_dict(credentials)
#
#     return jsonify(**files)
#
#
# @app.route('/authorize')
# def authorize():
#     flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
#       CLIENT_SECRETS_FILE, scopes=SCOPES)
#
#     flow.redirect_uri = url_for('oauth2callback', _external=True)
#
#     authorization_url, state = flow.authorization_url(
#         access_type='offline',
#         include_granted_scopes='true')
#
#     session['state'] = state
#
#     return redirect(authorization_url)
#
# @app.route('/oauth2callback')
# def oauth2callback():
#     state = session['state']
#
#     flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
#       CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
#     flow.redirect_uri = url_for('oauth2callback', _external=True)
#
#     authorization_response = request.url
#     flow.fetch_token(authorization_response=authorization_response)
#
#     credentials = flow.credentials
#     session['credentials'] = credentials_to_dict(credentials)
#
#     return redirect(flask.url_for('test_api_request'))
#
#
# @app.route('/revoke')
# def revoke():
#   if 'credentials' not in session:
#     return ('You need to <a href="/authorize">authorize</a> before ' +
#             'testing the code to revoke credentials.')
#
#   credentials = google.oauth2.credentials.Credentials(**session['credentials'])
#
#   revoke = requests.post('https://accounts.google.com/o/oauth2/revoke',
#       params={'token': credentials.token},
#       headers = {'content-type': 'application/x-www-form-urlencoded'})
#
#   status_code = getattr(revoke, 'status_code')
#   if status_code == 200:
#     return('Credentials successfully revoked.' + print_index_table())
#   else:
#     return('An error occurred.' + print_index_table())
#
# @app.route('/clear')
# def clear_credentials():
#   if 'credentials' in flask.session:
#     del flask.session['credentials']
#   return ('Credentials have been cleared.<br><br>' +
#           print_index_table())
#
#
# def credentials_to_dict(credentials):
#   return {'token': credentials.token,
#           'refresh_token': credentials.refresh_token,
#           'token_uri': credentials.token_uri,
#           'client_id': credentials.client_id,
#           'client_secret': credentials.client_secret,
#           'scopes': credentials.scopes}
#
# def print_index_table():
#   return ('<table>' +
#           '<tr><td><a href="/test">Test an API request</a></td>' +
#           '<td>Submit an API request and see a formatted JSON response. ' +
#           '    Go through the authorization flow if there are no stored ' +
#           '    credentials for the user.</td></tr>' +
#           '<tr><td><a href="/authorize">Test the auth flow directly</a></td>' +
#           '<td>Go directly to the authorization flow. If there are stored ' +
#           '    credentials, you still might not be prompted to reauthorize ' +
#           '    the application.</td></tr>' +
#           '<tr><td><a href="/revoke">Revoke current credentials</a></td>' +
#           '<td>Revoke the access token associated with the current user ' +
#           '    session. After revoking credentials, if you go to the test ' +
#           '    page, you should see an <code>invalid_grant</code> error.' +
#           '</td></tr>' +
#           '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
#           '<td>Clear the access token currently stored in the user session. ' +
#           '    After clearing the token, if you <a href="/test">test the ' +
#           '    API request</a> again, you should go back to the auth flow.' +
#           '</td></tr></table>')



###################################################################################

###################################################################################

###################################################################################





#
# @app.route('/')
# @login_required
# def index():
#     return render_template('index.html')
#
#
# @app.route('/add_volunteer', methods=['GET', 'POST'])
# def add_volunteer():
#     form = VolunteerForm(request.form)
#     if request.method == 'POST' and form.validate():
#
#         new_volunteer = Volunteer(
#             name = form.name.data,
#             email = form.email.data,
#             role = form.role.data
#         )
#
#         db.session.add(new_volunteer)
#         db.session.commit()
#
#         flash('Volunteer ' + new_volunteer.name + ' added!', 'success')
#
#         return redirect(url_for('index'))
#     return render_template('volunteer_form.html', form=form)
#
#
# @app.route('/volunteer/edit/<string:id>', methods=['GET', 'POST'])
# def edit_volunteer(id):
#
#     volunteer = Volunteer.query.get(id)
#     form = VolunteerForm(request.form, obj=volunteer)
#
#     if request.method == 'POST' and form.validate():
#         form.populate_obj(volunteer)
#
#         db.session.commit()
#
#         flash('Information from ' + volunteer.name + ' Updated', 'success')
#
#         return redirect(url_for('index'))
#     else:
#         return render_template('volunteer_form.html', form=form)
#
#
# @app.route('/volunteers')
# def volunteers():
#     volunteers = Volunteer.query.all()
#
#     if volunteers:
#         return render_template('volunteers.html', volunteers=volunteers)
#     else:
#         msg = 'No Records Found'
#         return render_template('volunteers.html', msg=msg)
#
#
# @app.route('/edit_user', methods=['GET', 'POST'])
# def edit_user():
#
#     user = User.query.get(1)
#     form = UserForm(request.form, obj=user)
#
#     if request.method == 'POST' and form.validate():
#         form.populate_obj(user)
#
#         db.session.commit()
#
#         flash('User login updated')
#
#         return redirect(url_for('index'))
#     else:
#         return render_template('user.html', form=form)
#
#
# @app.route('/add_user', methods=['GET', 'POST'])
# def new_user():
#
#     form = UserForm(request.form)
#
#     if request.method == 'POST' and form.validate():
#         new_user = User(
#             username = form.username.data,
#             password = form.password.data
#         )
#
#         db.session.add(new_user)
#         db.session.commit()
#
#         db.session.commit()
#
#         flash('User login updated')
#
#         return redirect(url_for('index'))
#     else:
#         return render_template('user.html', form=form)
#
# @app.route('/user/login', methods=['GET', 'POST'])
# def user_login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password_candidate = request.form['password']
#
#         user = User.query.filter_by(username=username).first()
#
#         if user:
#             if password_candidate == user.password:
#                 session['logged_in_user'] = True
#                 session['username'] = username
#                 # session['user'] = True
#
#                 flash('Your are now logged in as a volunteer', 'success')
#                 return redirect(url_for('index'))
#             else:
#                 error = 'Invalid login'
#                 return render_template('user_login.html', error=error)
#         else:
#             return render_template('user_login.html')
#             error='Username not found'
#             return render_template('user_login.html', error=error)
#     return render_template('user_login.html')
#
# # def is_logged_in(f):
# #     @wraps(f)
# #     def wrap(*args, **kwargs):
# #         if 'logged_in' in session:
# #             return f(*args, **kwargs)
# #         else:
# #             flash('Please log in to see this page', 'danger')
# #             return redirect(url_for('login'))
# #     return wrap
#
# def user_logged_in(f):
#     @wraps(f)
#     def wrap(*args, **kwargs):
#         if 'logged_in_user' in session:
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
if __name__ == '__main__':
    app.run()
