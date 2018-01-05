from flask import Flask, render_template, request, redirect, url_for
from config import DevConfig
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
# from flask_security.forms import RegisterForm, Required, StringField, ConfirmRegisterForm

app = Flask(__name__)
app.config.from_object(DevConfig)
app.config.from_object(DevConfig)
db = SQLAlchemy(app)

#Define models
roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    #
    # def __init__(self, name, description):
    #     self.name = name
    #     self. description = description
    #
    # def __str__(self):
    #     return self.name
    #
    # def __repr__(self):
    #     return "<Role '{}'>".format(self.name)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    # name = db.Column(db.String(100))
    # username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    # records = db.relationship('Record', backref='user', lazy='dynamic')

    # def __init__(self, username):
    #     self.username = username
    #
    # def __str__(self):
    #     return self.username
    #
    # def __repr__(self):
    #     return "<User '{}'>".format(self.username)


# class ExtendedRegisterForm(RegisterForm):
#     name = StringField('Name', [Required()])
#
# class ExtendedConfirmRegisterForm(ConfirmRegisterForm):
#     name = StringField('Name', [Required()])

# Setup flask_security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

class Record(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    date = db.Column(db.DateTime(), unique=True)
    volunteers = db.Column(db.String(255))
    notes = db.Column(db.Text())
    shopping_list = db.Column(db.Text())
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))

    def __init__(self, date):
        self.date = date

    def __repr__(self):
        return "<Record '{}'>".format(self.title)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/profile/<email>')
def profile(email):
    user = User.query.filter_by(email=email).first()
    return render_template('profile.html', user=user)

# @app.route('/post_user', methods=['POST'])
# def post_user():
#     print('enterrrriiinng')
#     if form.validate():
#         new_user = User(
#             username = request.form['username'],
#             email = request.form['email'],
#             name = request.form['name']
#         )
#         if new_user.isValid():
#             print('HEEELLOOOOOOOOO')
#             db.session.add(user)
#             db.session.commit()
#             return redirect(url_for('index'))
#         else:
#             print('not a viable user')
#             return '<h1>user info is not valid</h1>'
#     else:
#         print('not a valid form')
#         return '<h1>form info is not valid</h1>'


if __name__ == '__main__':
    app.run()
