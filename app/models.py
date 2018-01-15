from flask import Flask
from app import db

class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)


    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return "<User'{}'>".format(self.username)

openhour_volunteers = db.Table('openhour_volunteers',
    db.Column('openhour_id', db.Integer, db.ForeignKey('openhour.id')),
    db.Column('volunteer_id', db.Integer, db.ForeignKey('volunteer.id'))
)

class Volunteer(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))
    role = db.Column(db.String(50))
    email = db.Column(db.String(255), unique=True, nullable=False)
    openhours = db.relationship('Openhour', secondary=openhour_volunteers, backref='ohvolunteers', lazy='subquery')
    notes = db.relationship('Note', backref='openhour', lazy=True)


    def __init__(self, name, email, role):
        self.name = name
        self.email = email
        self.role = role

    def __repr__(self):
        return "<Volunteer '{}'>".format(self.name)

class Openhour(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    # author = db.Column(db.Integer(), db.ForeignKey('volunteer.id'))
    # author = db.Column(db.String(255))
    date = db.Column(db.DateTime())
    volunteers = db.relationship('Volunteer', secondary=openhour_volunteers, backref='openhourvols', lazy='dynamic')
    notes = db.relationship('Note', backref='openhournotes', lazy=True)
    # volunteers = db.Column(db.String(255))
    # customers = db.Column(db.Integer())
    # notes = db.Column(db.Text())
    # shopping = db.Column(db.Text())

    def __init__(self, date):
        # self.author = author
        self.date = date
        # self.volunteer = volunteer
        # self.customers = customers
        # self.notes = notes
        # self.shopping = shopping

    def __repr__(self):
        return "<Openhour '{}'>".format(self.date)

class Note(db.Model):
    id=db.Column(db.Integer(), primary_key=True)
    openhour_id = db.Column(db.Integer, db.ForeignKey('openhour.id'), nullable=False)
    author = db.Column(db.Integer(), db.ForeignKey('volunteer.id'))
    customers = db.Column(db.Integer())
    body = db.Column(db.Text())
    shopping = db.Column(db.Text())

class Email(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    send_date = db.Column(db.DateTime())
    recipients = db.Column(db.String(255))
    subject = db.Column(db.String(255))
    message = db.Column(db.Text())

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    tokens = db.Column(db.Text)
    active = db.Column(db.Boolean, default=False)
