import os

basedir = os.path.abspath(os.path.dirname(__file__))


# Default config class
class BaseConfig(object):
    DEBUG = False
    SECRET_KEY = 'S\x883\xc6\x01\x07\xc5 \r\xd8\xab\\\xc4{$\xdf\xc6-\x8a\xd1\x85\xd1j'


# Test config class that inherits from the default config class
class TestingConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False


# Development config class that inherits from the default config class
class DevelopmentConfig(BaseConfig):
    DEBUG = True


# Production config class that inherits from the default config class
class ProductionConfig(BaseConfig):
    DEBUG = False
