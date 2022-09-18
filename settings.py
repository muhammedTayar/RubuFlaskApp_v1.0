import os

class BaseConfig:
    """Base configuration"""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.urandom(24)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'm.tayyar61@gmail.com'
    MAIL_PASSWORD = 'Trabzonspor_61'
    RECAPTCHA_ENABLED = True
    RECAPTCHA_SITE_KEY = '6LeEzTAeAAAAAGwXrZQdJ4Vz_H60yB9FaOg8auSU'
    RECAPTCHA_SECRET_KEY = '6LeEzTAeAAAAAColEEDt6AV_PnB1JO0OSqRH_j_y'

class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    DEBUG = True
    ENV = 'development'