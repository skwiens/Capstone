#app/users/views/py

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from app.models import User
from app.forms import UserForm
from app import db

users_blueprint = Blueprint('users', __name__, template_folder='templates')

@users_blueprint.route('/')
def users():
    users = User.query.all()

    if users:
        return render_template('users.html', users=users)
    else:
        msg = 'No Users Found'
        return render_template('users.html', msg=msg)

@users_blueprint.route('/new', methods=['GET', 'POST'])
def new_volunteer():
    form = UserForm(request.form)
    if request.method == 'POST' and form.validate():

        new_user = User(
            username = form.username.data,
            password = form.password.data
        )

        db.session.add(new_user)
        db.session.commit()

        flash('New user created with username: %s' % new_user.username, 'success')

        return redirect(url_for('index'))
    return render_template('user_form.html', form=form)

@users_blueprint.route('/1/edit', methods=['GET', 'POST'])
def edit_user():
    form = UserForm(request.form)

    # If a user exists, return the first user. If not, create a user to prepopulate the form
    if User.query.get(1):
        user = User.query.get(1)
    else:
        user = User(username='username', password='password')
        db.session.add(user)

    form = UserForm(request.form, obj=user)

    if request.method == 'POST' and form.validate():
        form.populate_obj(user)
        db.session.commit()

        flash('User Login information updated', 'success')
        return redirect(url_for('index'))
    else:
        return render_template('user_form.html', form=form)

@users_blueprint.route('/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user:
            if password_candidate == user.password:
                session['user'] = True

                flash('You are now logged in as a volunteer', 'success')

                return redirect(url_for('index'))
            else:
                error = 'Invalid login'
                return render_template('user_login.html', error=error)
        else:
            error = 'Username not found'
            return render_template('user_login.html', error=error)

    return render_template('user_login.html')
