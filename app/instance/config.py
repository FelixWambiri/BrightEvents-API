# Default config class
import os


class BaseConfig(object):
    DEBUG = False
    CSRF_ENABLED = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = 'felowambiri@gmail.com'


class TestingConfig(BaseConfig):
    """ Testing configurations"""
    DEBUG = True
    TESTING = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URI')


class DevelopmentConfig(BaseConfig):
    """ Development configurations"""
    DEBUG = True


class ProductionConfig(BaseConfig):
    """ Production configurations"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_ECHO = False


app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

}
