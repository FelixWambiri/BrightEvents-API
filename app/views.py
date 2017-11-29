from flask import Flask, request, jsonify, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from app.models.event import Event
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


# Logout route
@app.route('/api/v1/logout')
@login_required
def logout():
    logout_user()
    return jsonify({"success": 'You are logged out'})


# User crud operations
# Create an event
@app.route('/api/v1/create_events', methods=['POST'])
@login_required
def create_events():
    data = request.get_json()
    name = data['name']
    category = data['category']
    location = data['location']
    owner = data['owner']
    description = data['description']
    if name is None or category is None or location is None or owner is None:
        abort(400)
    event = Event(name=name, category=category, location=location, owner=owner, description=description)
    try:
        current_user.create_event(event)
        user_accounts.add_all_individual_events(current_user)
        return jsonify({"Success": "Event created successfully"})
    except KeyError:
        return jsonify({"Warning": 'The event already exists'})


if __name__ == '__main__':
    app.run()
