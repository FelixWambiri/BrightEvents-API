from flask import Flask
from flask_login import LoginManager

app = Flask(__name__)

# Import the apps configuration settings from config file in instance folder
app.config.from_object('app.instance.config.DevelopmentConfig')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:AndelaFellow2017@localhost/BrightEventDb'
SQLALCHEMY_TRACK_MODIFICATIONS = True

# Create login manager class
login_manager = LoginManager()

# Configure login
login_manager.init_app(app)

# View to be directed to for unauthorized attempt to access a protected page
login_manager.login_view = "/api/v1/login"

# Message flashed for unauthorized attempt to access a protected page
login_manager.login_message = u"Please Login First to access this resource"
login_manager.login_message_category = "info"
