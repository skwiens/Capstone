from flask import Flask, render_template
from config import DevConfig
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(DevConfig)
app.config.from_object(DevConfig)
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    records = db.relationship('Record', backref='user', lazy='dynamic')

    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return "<User '{}'>".format(self.username)

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
    # return '<h1>hello world</h1>'
    return render_template('index.html')

if __name__ == '__main__':
    app.run()
