import os
# basedir = os.path.abspath(os.path.dirname(__file__))

class Auth:
    CLIENT_ID = os.environ['CLIENT_ID']
    CLIENT_SECRET = os.environ['CLIENT_SECRET']
    REDIRECT_URI = 'http://localhost:5000/oauth2callback'
    AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
    USER_INFO = 'https://www.googleapis.com/userinfo/v2/me'
    SCOPE = []

class AppConfig:
    APP_NAME = "Bethany Food Bank"
    SECRET_KEY = 'clavesecreto'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    CLIENT_SECRETS_FILE = os.environ['CLIENT_SECRETS_FILE']

# class DevConfig(Config):
#     DEBUG = True
#
#
# class ProdConfig(Config):
#     DEBUG = False
#     SQLALCHEMY_DATABASE_URI = 'mysql://lola:lilly@localhost/food_bank'








# import os
# basedir = os.path.abspath(os.path.dirname(__file__))
#
# class Config(object):
#     DEBUG = False
#     TESTING = False
#     CSRF_ENABLED = True
#
#
# class ProdConfig(Config):
#     pass
#
# class DevConfig(Config):
    # DEBUG = True
    # SQLALCHEMY_DATABASE_URI = 'mysql://lola:lilly@localhost/food_bank'
    # SECRET_KEY = 'clavesecreto'
    # SECURITY_REGISTERABLE = True
    # # SECURITY_PASSWORD_SALT = 'saltygoodness'
    # # SECURITY_CONFIRMABLE = False
    # CSRF_ENABLED = True
    # USER_ENABLE_EMAIL = False
