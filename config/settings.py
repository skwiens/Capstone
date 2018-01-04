import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True


class ProdConfig(Config):
    pass

class DevConfig(Config):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI = 'mysql://lola:lilly@localhost/food_bank'
    SECRET_KEY = 'clavesecreto'
