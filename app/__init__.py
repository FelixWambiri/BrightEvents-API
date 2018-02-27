from flask import Flask

from app.init_db import db
from flask_mail import Mail

from app.instance.config import app_config
from app.models.event import Event

mail = Mail()


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    db.init_app(app)
    mail.init_app(app)
    app.register_blueprint(auth_blueprint, url_prefix='/api/auth')
    app.register_blueprint(event_blueprint, url_prefix='/api')
    return app


from app.auth import auth as auth_blueprint
from app.events import event as event_blueprint
