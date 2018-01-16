"""
To write command-line tasks belonging outside the web app itself
"""
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

# Getting the flask instance
from app import app
from app.init_db import db

app.config.from_object('app.instance.config.DevelopmentConfig')

migrate = Migrate(app, db)

# Manager instance
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
