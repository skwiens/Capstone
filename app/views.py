# app/views.py
from flask import Flask, render_template, request, url_for, redirect, session, flash
from . import app
from .forms import VolunteerForm, OpenhourForm, UserForm, EmailForm, NoteForm
from .models import Volunteer, Openhour, User, Email, Note
from app import db
from functools import wraps
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from requests_oauthlib import OAuth2Session
from .config import Auth

# FOR GMAIL API SENDING EMAILS:
##########################################
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
#################################

import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
# import sendgrid
# from sendgrid.helpers.mail import *


#### HELP!  NEED THIS TO BE NOT A FILE! #####
CLIENT_SECRETS_FILE = 'client_secret.json'
CLIENT_SECRET_FILE = 'client_secret.json'
# CLIENT_SECRETS_FILE = os.environ['CLIENT_SECRETS_FILE']
SCOPES = ['https://www.googleapis.com/auth/gmail.compose', 'https://www.googleapis.com/auth/calendar']
API_SERVICE_NAME = 'gmail'
API_VERSION = 'v1'
APPLICATION_NAME = 'Bethany Food Bank'

import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'gmail-python-email-send.json')
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        print('Storing gmail credentials to ' + credential_path)
    return credentials

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

# @app.route('/edit_user', methods=['GET', 'POST'])
# # @admin_logged_in
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
#         flash('User login updated', 'success')
#
#         return redirect(url_for('index'))
#     else:
#         return render_template('user.html', form=form)


# @app.route('/add_user', methods=['GET', 'POST'])
# # @admin_logged_in
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
#         flash('User login updated', 'success')
#
#         return redirect(url_for('index'))
#     else:
#         return render_template('user.html', form=form)

# @app.route('/user_login', methods=['GET', 'POST'])
# def user_login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password_candidate = request.form['password']
#
#         user = User.query.filter_by(username=username).first()
#
#         if user:
#             if password_candidate == user.password:
#                 session['user'] = 'volunteer'
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


# @app.route('/add_openhour', methods=['GET', 'POST'])
# # @user_logged_in
# def add_openhour():
#     form = OpenhourForm(request.form)
#
#     volunteer_list = [(volunteer.id, volunteer.name) for volunteer in Volunteer.query.all()]
#     form.volunteers.choices = volunteer_list
#
#     if request.method == 'POST' and form.validate():
#         new_openhour = Openhour(
#             # author = form.author.data,
#             date = form.date.data,
#             # volunteer = Volunteer.query.get(form.volunteer.data)
#             # customers = form.customers.data,
#             # notes = form.notes.data,
#             # shopping = form.shopping.data
#         )
#
#         db.session.add(new_openhour)
#
#         for volunteer in form.volunteers.data:
#             new_openhour.volunteers.append(Volunteer.query.get(volunteer))
#
#         # new_openhour.volunteers.append(Volunteer.query.get(form.volunteers.data))
#
#         db.session.commit()
#
#         flash('Record for ' + new_openhour.date.strftime('%m/%d/%Y') + 'saved! Thank you for volunteering with us!', 'success')
#
#         return redirect(url_for('index'))
#
#     return render_template('add_openhour.html', form=form)


# @app.route('/openhours')
# # @admin_logged_in
# def openhours():
#     openhours = Openhour.query.all()
#
#     if openhours:
#         return render_template('openhours.html', openhours=openhours)
#     else:
#         msg = 'No Open Hours Found'
#         return render_template('openhours.html', msg=msg)

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

@app.route('/openhour/<string:id>/add_note', methods=['GET', 'POST'])
def add_note(id):
    form = NoteForm(request.form)

    volunteer_list = [(volunteer.id, volunteer.name) for volunteer in Volunteer.query.all()]

    openhour = Openhour.query.get(id)

    form.author.choices = volunteer_list

    if request.method == 'POST' and form.validate():
        new_note = Note(
            openhour_id = id,
            author = form.author.data,
            customers = form.customers.data,
            body = form.body.data,
            shopping = form.shopping.data
        )

        db.session.add(new_note)
        db.session.commit()


        sender = 'xana.wines@gmail.com'
        subject = 'Open Hour: ' + openhour.date.strftime('%m/%d/%Y')
        msgHtml = new_note.shopping
        msgPlain = new_note.shopping
        recipients = []

        for volunteer in openhour.volunteers:
            recipients.append(volunteer.email)

        to = ','.join(recipients)

        SendMessage(sender, to, subject, msgHtml, msgPlain)

        # for volunteer in openhour.volunteers:
        #     to = volunteer.email
        #     SendMessage(sender, to, subject, msgHtml, msgPlain)

        flash('Notes created for' + openhour.date.strftime('%m/%d/%Y') + '. Thank You!', 'success')

        # flash('Notes created for' + Openhour.query.get(id).date.strftime('%m/%d/%Y') + '. Thank You!', 'success')

        return redirect(url_for('index'))

    return render_template('add_note.html', form=form)

@app.route('/openhour/<string:id>/note')
def note(id):
    openhour = Openhour.query.get(id)
    note = openhour.notes[0]

    return render_template('note.html', note=note, openhour=openhour)

def CreateMessageHtml(sender, to, subject, msgHtml, msgPlain):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to
    msg.attach(MIMEText(msgPlain, 'plain'))
    msg.attach(MIMEText(msgHtml, 'html'))
    # return {'raw': base64.urlsafe_b64encode(msg.as_string())}
    return {'raw': base64.urlsafe_b64encode(msg.as_string().encode()).decode('ascii')}

def SendMessage(sender, to, subject, msgHtml, msgPlain, attachmentFile=None):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    # if attachmentFile:
    #     message1 = createMessageWithAttachment(sender, to, subject, msgHtml, msgPlain, attachmentFile)
    # else:
    #     message1 = CreateMessageHtml(sender, to, subject, msgHtml, msgPlain)
    # result = SendMessageInternal(service, "me", message1)
    if 'user' in session and session['user'] == 'admin':
        message1 = CreateMessageHtml(sender, to, subject, msgHtml, msgPlain)
        result = SendMessageInternal(service, "me", message1)
        return result
    else:
        redirect(url_for('admin_login'))

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
    # return {'raw': base64.urlsafe_b64encode(msg.as_string())}
    return {'raw': base64.urlsafe_b64encode(msg.as_string().encode()).decode('ascii')}

def createMessageWithAttachment(
    sender, to, subject, msgHtml, msgPlain, attachmentFile):
    """Create a message for an email.

    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      msgHtml: Html message to be sent
      msgPlain: Alternative plain text message for older email clients
      attachmentFile: The path to the file to be attached.

    Returns:
      An object containing a base64url encoded email object.
    """
    message = MIMEMultipart('mixed')
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    messageA = MIMEMultipart('alternative')
    messageR = MIMEMultipart('related')

    messageR.attach(MIMEText(msgHtml, 'html'))
    messageA.attach(MIMEText(msgPlain, 'plain'))
    messageA.attach(messageR)

    message.attach(messageA)

    print("create_message_with_attachment: file: %s" % attachmentFile)
    content_type, encoding = mimetypes.guess_type(attachmentFile)

    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)
    if main_type == 'text':
        fp = open(attachmentFile, 'rb')
        msg = MIMEText(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'image':
        fp = open(attachmentFile, 'rb')
        msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'audio':
        fp = open(attachmentFile, 'rb')
        msg = MIMEAudio(fp.read(), _subtype=sub_type)
        fp.close()
    else:
        fp = open(attachmentFile, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()
    filename = os.path.basename(attachmentFile)
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)

    return {'raw': base64.urlsafe_b64encode(message.as_string())}

@app.route('/send_email')
@admin_logged_in
def send_email():
    email = Email.query.get(1)
    to = email.recipients
    sender = "xana.wines.ada@gmail.com"
    subject = email.subject
    msgHtml = email.message
    msgPlain = email.message
    # to = "xana.wines.ada@gmail.com"
    # sender = "xana.wines.ada@gmail.com"
    # subject = "subject"
    # msgHtml = "Hi<br/>Html Email"
    # msgPlain = "Hi\nPlain Email"
    SendMessage(sender, to, subject, msgHtml, msgPlain)
    # # Send message with attachment:
    # # SendMessage(sender, to, subject, msgHtml, msgPlain, '/path/to/file.pdf')
    flash('Email successfully sent!', 'success')
    return redirect(url_for('index'))


    # home_dir = os.path.expanduser('~')
    # credential_dir = os.path.join(home_dir, '.credentials')
    # if not os.path.exists(credential_dir):
    #     os.makedirs(credential_dir)
    # credential_path = os.path.join(credential_dir, 'gmail-python-email-send.json')
    # store = oauth2client.file.Storage(credential_path)
    # credentials = store.get()
    # if not credentials or credentials.invalid:
    #     flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
    #     flow.user_agent = APPLICATION_NAME
    #     credentials = tools.run_flow(flow, store)
    #     print('Storing gmail credentials to ' + credential_path)
    # return credentials



def get_cal_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    credentials = google.oauth2.credentials.Credentials(
      **session['credentials'])
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python.json')

    store = oauth2client.file.Storage(credential_path)
    # credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        print('Storing calendar credentials to ' + credential_path)
    return credentials

@app.route('/make_appt')
@admin_logged_in
def make_appt():

    credentials = google.oauth2.credentials.Credentials(
      **session['credentials'])

    # service = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)


    # credentials = get_cal_credentials()
    # credentials = get_credentials()
    # http = credentials.authorize(httplib2.Http())
    # service = discovery.build('calendar', 'v3', http=http)

    event = {
        'summary': 'OH: Nathan K.',
        'start': {
            'dateTime': '2018-01-22T17:35:09-08:00',
            'timeZone': 'America/Los_Angeles'
        },
        'end': {
            'dateTime': '2018-01-22T17:35:09-08:00',
            'timeZone': 'America/Los_Angeles'
        }
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    print ('Event created: %s' % (event.get('htmlLink')))
    flash('Event created: %s' % (event.get('htmlLink')), 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
