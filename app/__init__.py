from flask_sqlalchemy import SQLAlchemy
from flask import Flask


from app.instance.config import app_config

# Initialize sql-alchemy
db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    db.init_app(app)

    return app




