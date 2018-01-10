from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from .config import app_config
from flask_login import LoginManager

app = Flask(__name__, instance_relative_config=True)

# app.config.from_object(app_config['dev'])
#
# app.config.from_pyfile('config.py')

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view="login"
login_manager.session_protection = "strong"

from app import views
from app import models
from app import forms
