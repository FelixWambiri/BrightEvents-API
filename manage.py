"""
To write command-line tasks belonging outside the web app itself
"""
import os
import unittest

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

# Getting the flask instance
from app import db, create_app

app = create_app(config_name=os.getenv('APP_SETTINGS'))

migrate = Migrate(app, db)

# Manager instance
manager = Manager(app)
manager.add_command('db', MigrateCommand)


# Define our command for testing called testing
@manager.command
def test():
    """Runs the unit tests"""
    tests = unittest.TestLoader().discover('./tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


if __name__ == '__main__':
    manager.run()
