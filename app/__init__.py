from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, instance_relative_config=True)

db = SQLAlchemy(app)

from app import views
from app import models
from app import forms

app.config.from_object('config')
app.config.from_pyfile('config.py')
