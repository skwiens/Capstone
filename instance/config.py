import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Auth:
    CLIENT_ID = ('127636107416-n5806tr841p9445dd5h5t7nm21l7jeie.apps.googleusercontent.com')
    CLIENT_SECRET = ('6kVn4zUH4RMRLAyrN3VtTJ0A')
    REDIRECT_URI = 'http://localhost:5000/oauth2callback'
    AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
    USER_INFO = 'https://www.googleapis.com/userinfo/v2/me'
    SCOPE = []

class Config:
    APP_NAME = "Bethany Food Bank"
    SECRET_KEY = 'clavesecreto'

class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://lola:lilly@localhost/food_bank'

class ProdConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://lola:lilly@localhost/food_bank'

app_config = {
    "dev": DevConfig,
    "prod": ProdConfig,
    "default": DevConfig
}



# DEBUG = True
# SECRET_KEY = 'clavesecreto'
# SQLALCHEMY_DATABASE_URI = 'mysql://lola:lilly@localhost/food_bank'
