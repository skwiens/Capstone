#app/open_hours/views.py

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from app.models import Openhour, Volunteer, Note
from app.forms import OpenhourForm, NoteForm
from app import db
from app.views import admin_logged_in, user_logged_in

import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

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
import google_auth_httplib2

CLIENT_SECRETS_FILE = 'client_secret.json'
# CLIENT_SECRET_FILE = 'client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/gmail.compose', 'https://www.googleapis.com/auth/calendar']
APPLICATION_NAME = 'Bethany Food Bank'


openhours_blueprint = Blueprint('openhours', __name__, template_folder='templates')


def get_credentials():
    if 'credentials' not in session:
        return redirect('authorize')

    credentials = google.oauth2.credentials.Credentials(
      **session['credentials'])
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'gmail-python-email-send.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    print('^^^^^^^^^^^^^^^^')
    if not credentials or credentials.invalid:
        print('ENTERING!!! CREATING CREDENTIALS!!!!')
        flow = client.flow_from_clientsecrets(CLIENT_SECRETS_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        print('Storing calendar credentials to ' + credential_path)
    return credentials

# @app.route('/authorize')
def authorize():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES)

    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')

    session['state'] = state

    return redirect(authorization_url)

# @app.route('/oauth2callback')
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

@openhours_blueprint.route('/')
def openhours():
    openhours = Openhour.query.all()

    if openhours:
        return render_template('openhours.html', openhours=openhours)
    else:
        msg = 'No Open Hours Found'
        return render_template('openhours.html', msg=msg)

# @openhours_blueprint.route('/<string:id>')
# def show_openhour(id):
#     openhour = Openhour.query.get(id)
#
#     if openhour:
#         return render_template('show_openhour.html')
#     else:
#         #render 404 not Found


@openhours_blueprint.route('/new', methods=['GET', 'POST'])
@admin_logged_in
def new_openhour():
    form = OpenhourForm(request.form)

    #Dynamically create a list of volunteers to select for the openhour
    volunteer_list = [(volunteer.id, volunteer.name) for volunteer in Volunteer.query.filter(Volunteer.role != 'shopper').all()]
    form.volunteers.choices = volunteer_list
    form.volunteers.choices.insert(0, (-1, 'None'))

    shopper_list = [(volunteer.id, volunteer.name) for volunteer in Volunteer.query.filter(Volunteer.role != 'open-hours').all()]
    form.shoppers.choices = shopper_list
    form.shoppers.choices.insert(0, (-1, 'None'))

    if request.method == 'POST' and form.validate():
        new_openhour = Openhour(date=form.date.data)

        db.session.add(new_openhour)

        # Add in any volunteers and shoppers
        for volunteer in form.volunteers.data:
            if volunteer != -1:
                new_openhour.volunteers.append(Volunteer.query.get(volunteer))

        for shopper in form.shoppers.data:
            if volunteer != -1:
                new_openhour.shoppers.append(Volunteer.query.get(shopper))

        db.session.commit()

        flash('Record for %s saved! Thank you for volunteering with us!' % new_openhour.date.strftime('%m/%d/%Y'), 'success')

        return redirect(url_for('index'))

    return render_template('openhour_form.html', form=form)

@openhours_blueprint.route('/<string:id>/edit', methods=['GET', 'POST'])
@admin_logged_in
def edit_openhour(id):
    openhour = Openhour.query.get(id)
    form = OpenhourForm(request.form, obj=openhour)

    #Dynamically create a list of volunteers to select for the openhour
    volunteer_list = [(volunteer.id, volunteer.name) for volunteer in Volunteer.query.filter(Volunteer.role != 'shopper').all()]
    form.volunteers.choices = volunteer_list
    form.volunteers.choices.insert(0, (-1, 'None'))

    shopper_list = [(volunteer.id, volunteer.name) for volunteer in Volunteer.query.filter(Volunteer.role != 'open-hours').all()]
    form.shoppers.choices = shopper_list
    form.shoppers.choices.insert(0, (-1, 'None'))

    if request.method == 'POST' and form.validate():
        form.populate_obj(openhour)
        db.session.commit()

        flash('Openhour for %s updated!' % openhour.date.strftime('%m/%d/%Y'), 'success')

        return redirect(url_for('index'))

    return render_template('openhour_form.html', form=form)

@openhours_blueprint.route('/<string:id>/post', methods=['GET', 'POST'])
# @admin_logged_in
def post_openhour(id):
    ### POST TO GOOGLE calendar

    ####### WORKS IF DONE WITHIN THE HOUR#################
    # credentials = google.oauth2.credentials.Credentials(**session['credentials'])
    # service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)

    #### INSUFFICIENT PERMISSION########
    ##############################################
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    ##############################################

    openhour = Openhour.query.get(id)

    date = '{:%Y-%m-%d}'.format(openhour.date)

    # Post to calendar
    for volunteer in openhour.volunteers:
        event = {
            'summary': 'OH: %s' % volunteer.name,
            'start': {
                'date': date
            },
            'end': {
                'date': date
            }
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        print ('Event created: %s' % (event.get('htmlLink')))
        # try:
        #     service.events().insert(calendarId='primary', body=calevent).execute()
        #     print('Event created: %s' % (event.get('htmlLink')))
        # except google.auth.exceptions.RefreshError:
        #     flash('An error occurred. Please log out, login and try again', 'danger')

    for shopper in openhour.shoppers:
        event = {
            'summary': 'SHOP: %s' % shopper.name,
            'start': {
                'date': date
            },
            'end': {
                'date': date
            }
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        print ('Event created: %s' % (event.get('htmlLink')))

    return redirect(url_for('index'))

@openhours_blueprint.route('/<string:id>/notes/new', methods=['GET', 'POST'])
def new_notes(id):
    form = NoteForm(request.form)
    form.author.choices = [(volunteer.id, volunteer.name) for volunteer in Volunteer.query.all()]
    form.author.choices.insert(0, (-1, 'Select your name'))

    openhour = Openhour.query.get(id)

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

        # Send email based on the Notes
        ##[ ] Turn this email msg into a template version to send
        # sender = 'xana.wines@gmail.com'
        # subject = 'Open Hour: ' + openhour.date.strftime('%m/%d/%Y')
        # msgHtml = new_note.shopping
        # msgPlain = new_note.shopping
        # recipients = []
        #
        # for volunteer in openhour.volunteers:
        #     recipients.append(volunteer.email)
        #
        # to = ','.join(recipients)
        #
        # SendMessage(sender, to, subject, msgHtml, msgPlain)

        flash('Notes created for %s. Thank you!' % openhour.date.strftime('%m/%d/%Y'), 'success')

        return redirect(url_for('index'))

    return render_template('notes_form.html', form=form)

@openhours_blueprint.route('/<string:id>/notes')
def notes(id):
    openhour = Openhour.query.get(id)
    notes = openhour.notes[0]
    author = Volunteer.query.get(notes.author)

    return render_template('notes.html', notes=notes, openhour=openhour, author=author)
