from flask import Blueprint, flash, redirect, render_template, request, url_for
from app.models import Volunteer
from app.forms import VolunteerForm
from app import db


volunteers_blueprint = Blueprint('volunteers', __name__, template_folder='templates')

@volunteers_blueprint.route('/')
def volunteers():
    volunteers = Volunteer.query.all()

    if volunteers:
        return render_template('volunteers.html', volunteers=volunteers)
    else:
        msg = 'No Volunteers Found'
        return render_template('volunteers.html', msg=msg)
    return render_template('volunteers.html')

@volunteers_blueprint.route('/new', methods=['GET', 'POST'])
# @admin_logged_in
def new_volunteer():
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

@volunteers_blueprint.route('/<string:id>/edit', methods=['GET', 'POST'])
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
