from flask import Flask, request, jsonify, abort
from flask_login import LoginManager, login_user

from app.models.user import User
from app.models.user_accounts import UserAccounts

app = Flask(__name__)

# Import the apps configuration settings from config file in instance folder
app.config.from_object('app.instance.config.DevelopmentConfig')

# Create login manager class
login_manager = LoginManager()

# Configure login
login_manager.init_app(app)

# View to be directed to for unauthorized attempt to access a protected page
login_manager.login_view = "/api/v1/login"

# Message flashed for unauthorized attempt to access a protected page
login_manager.login_message = u"Please Login First to access this page"
login_manager.login_message_category = "info"

# User accounts object
user_accounts = UserAccounts()


# Callback method to reload the user object
@login_manager.user_loader
def load_user(username):
    return user_accounts.get_specific_user(username)


# Registration route
# All fields must be filled
@app.route('/api/v1/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']
    confirm_password = data['confirm_password']
    if username is None or email is None or password is None or confirm_password is None:
        abort(400)
    if user_accounts.get_specific_user(username):
        return jsonify({"msg": "User already exists, choose another username"})
    else:
        user = User(username=username, email=email, password=password, confirm_password=confirm_password)
        user_accounts.create_user(user)
        response = jsonify({"msg": "You have been registered successfully and can proceed to login"})
        response.status_code = 201
        return response


# Login route
@app.route('/api/v1/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password_f = data['password']
    if username is None or password_f is None:
        abort(400)
    if user_accounts.get_specific_user(username):
        if password_f == user_accounts.get_specific_user(username).password:
            login_user(user_accounts.get_specific_user(username))
            response = jsonify({"Success": "You were successfully logged in"})
            response.status_code = 200
            return response

        else:
            return jsonify({"Warning": 'Invalid Password'})

    else:
        return jsonify({"Warning": 'Invalid Username, The Username does not exist'})


if __name__ == '__main__':
    app.run()
