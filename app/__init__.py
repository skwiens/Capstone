#app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import AppConfig
from flask_login import LoginManager
from flask_migrate import Migrate

app = Flask(__name__, instance_relative_config=True)

app.config.from_object(AppConfig)
# app.config.from_pyfile('config.py')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view="login"
login_manager.session_protection = "strong"

from app import views
from app import models
from app import forms

# import the blueprints
from app.volunteers.views import volunteers_blueprint
from app.users.views import users_blueprint
from app.open_hours.views import openhours_blueprint


# register the blueprints
app.register_blueprint(volunteers_blueprint, url_prefix='/volunteers')
app.register_blueprint(users_blueprint, url_prefix='/users')
app.register_blueprint(openhours_blueprint, url_prefix='/openhours')

if __name__ == '__main__':
    app.run()
