# Default config class
class BaseConfig(object):
    DEBUG = False
    CSRF_ENABLED = False
    SECRET_KEY = 'S\x883\xc6\x01\x07\xc5 \r\xd8\xab\\\xc4{$\xdf\xc6-\x8a\xd1\x85\xd1j'
    # SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:AndelaFellow2017@localhost/BrightEventDb'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ECHO = True


class TestingConfig(BaseConfig):
    """ Testing configurations"""
    DEBUG = True
    TESTING = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    # SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:AndelaFellow2017@localhost/BrightEventTestDb'


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
