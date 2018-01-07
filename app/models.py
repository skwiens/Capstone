from flask import Flask
from app import db

class Volunteer(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))
    role = db.Column(db.String(50))
    email = db.Column(db.String(255), unique=True, nullable=False)
    # records = db.relationship('Record', backref='volunteer', lazy='dynamic')

    def __init__(self, name, email, role):
        self.name = name
        self.email = email
        self.role = role

    def __repr__(self):
        return "<Volunteer '{}'>".format(self.name)

class Record(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    # author = db.Column(db.Integer(), db.ForeignKey('volunteer.id'))
    author = db.Column(db.String(255))
    date = db.Column(db.DateTime())
    volunteers = db.Column(db.String(255))
    customers = db.Column(db.Integer())
    notes = db.Column(db.Text())
    shopping = db.Column(db.Text())

    def __init__(self, author, date, volunteers, customers, notes, shopping):
        self.author = author
        self.date = date
        self.volunteers = volunteers
        self.customers = customers
        self.notes = notes
        self.shopping = shopping

    def __repr__(self):
        return "<Record '{}'>".format(self.title)
