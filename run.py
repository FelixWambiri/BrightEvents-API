"""
To write command-line tasks belonging outside the web app itself
"""
from flask_script import Manager

# Getting the flask instance
from app.views import app

# Manager instance
manager = Manager(app)

if __name__ == '__main__':
    manager.run()
