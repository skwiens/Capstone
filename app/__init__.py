from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import app_config

app = Flask(__name__, instance_relative_config=True)

app.config.from_object(app_config['prod'])
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)

from app import views
from app import models
from app import forms
