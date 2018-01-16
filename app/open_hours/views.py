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
