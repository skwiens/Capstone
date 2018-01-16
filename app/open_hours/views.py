#app/open_hours/views.py

from flask import Blueprint, flash, redirect, render_template, request, url_for
from app.models import Openhour, Volunteer
from app.forms import OpenhourForm
from app import db

openhours_blueprint = Blueprint('openhours', __name__, template_folder='templates')

@openhours_blueprint.route('/')
def openhours():
    openhours = Openhour.query.all()

    if openhours:
        return render_template('openhours.html', openhours=openhours)
    else:
        msg = 'No Open Hours Found'
        return render_template('openhours.html', msg=msg)

@openhours_blueprint.route('/new', methods=['GET', 'POST'])
def new_openhour():
    form = OpenhourForm(request.form)

    #Dynamically create a list of volunteers to select for the openhour
    volunteer_list = [(volunteer.id, volunteer.name) for volunteer in Volunteer.query.all()]
    form.volunteers.choices = volunteer_list

    if request.method == 'POST' and form.validate():
        new_openhour = Openhour(date=form.date.data)

        db.session.add(new_openhour)

        # Add in any volunteers
        for volunteer in form.volunteers.data:
            new_openhour.volunteers.append(Volunteer.query.get(volunteer))

        db.session.commit()

        flash('Record for %s saved! Thank you for volunteering with us!' % new_openhour.date.strftime('%m/%d/%Y'), 'success')

        return redirect(url_for('index'))

    return render_template('openhour_form.html', form=form)
