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
def load_user(email):
    return user_accounts.get_specific_user(email)


# Registration route
# All fields must be filled
@app.route('/api/v1/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']
    if username is None or email is None or password is None:
        abort(400)
    if user_accounts.get_specific_user(email):
        return jsonify({"Warning": "User already exists, choose another username"})
    else:
        user = User(username=username, email=email, password=password)
        user_accounts.create_user(user)
        response = jsonify({"Success": "You have been registered successfully and can proceed to login"})
        response.status_code = 201  # Created
        return response


# Login route
@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password_f = data['password']
    if email is None or password_f is None:
        abort(400)
    user = user_accounts.get_specific_user(email)
    if user:
        if user.compare_hashed_password(password_f):
            login_user(user_accounts.get_specific_user(email))
            response = jsonify({"Success": "You were successfully logged in"})
            response.status_code = 200  # Ok
            return response

        else:
            response = jsonify({"Warning": 'Invalid Credentials'})
            response.status_code = 401  # Unauthorized
            return response

    else:
        response = jsonify({"Warning": 'Invalid Credentials'})
        response.status_code = 401  # Unauthorized
        return response


# Logout route
@app.route('/api/v1/auth/logout')
@login_required
def logout():
    logout_user()
    response = jsonify({"success": 'You are logged out'})
    response.status_code = 200  # Ok


# User crud operations
# Create an event
@app.route('/api/v1/events', methods=['POST'])
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
        user_accounts.add_all_individual_events(None,current_user)
        response = jsonify({"Success": "Event created successfully",
                            "event": {"name": event.name, "category": event.category, "location": event.location,
                                      "owner": owner, "description": event.description}})
        response.status_code = 201  # Created
        return response
    except KeyError:
        return jsonify({"Warning": 'The event already exists'})


# Update an Event
# Name field should not be editable
@app.route('/api/v1/events/<string:event_name>', methods=['PUT'])
@login_required
def update_events(event_name):
    data = request.get_json()
    new_name = data['new_name']
    category = data['category']
    location = data['location']
    owner = data['owner']
    description = data['description']

    try:
        event = current_user.update_event(event_name, new_name=new_name, category=category, location=location,
                                          owner=owner,
                                          description=description)
        user_accounts.add_all_individual_events(event_name, current_user)
        return jsonify({'success': 'The event has been updated successfully',
                        "event": {"name": event.name, "category": event.category, "location": event.location,
                                  "owner": owner, "description": event.description}})
    except KeyError:
        response = jsonify({'warning': 'The event does not exist'})
        response.status_code = 404  # Not found
        return response


# Delete an event from both the personal events list and the public events list"
@app.route('/api/v1/events/<string:event_name>', methods=['DELETE'])
@login_required
def delete_events(event_name):
    try:
        current_user.delete_event(event_name)
        user_accounts.delete_an_individuals_events(event_name)
        response = jsonify({"Success": "Event deleted successfully"})
        response.status_code = 204
        return response
    except KeyError:
        response = jsonify({'warning': 'The event does not exist'})
        response.status_code = 404  # Not found
        return response

        # Retrieves all events


# Route to display all events
@app.route('/api/v1/events', methods=['GET'])
@login_required
def get_all_events():
    if current_user.get_number_of_events() > 0:
        # list to store all events
        events = []
        for event in current_user.events_dict.values():
            # add events into list by  appending them
            events.append({'name': event.name, "category": event.category, "location": event.location})
        return jsonify({'Events': events})
    else:
        return jsonify({'Info': "No event created so far"})


# Route to rsvp to an event
@app.route('/api/v1/event/<event_name>/rsvp', methods=['POST'])
@login_required
def rsvp_event(event_name):
    event_dict = user_accounts.events
    event = event_dict.get(event_name)
    event.add_attendants(current_user.id, current_user.username)
    response = jsonify({'success': 'You have rsvp into an event successfully'})

    response.status_code = 200
    return response


# Route to reset password
@app.route('/api/auth/reset_password', methods=['POST'])
@login_required
def reset_password():
    data = request.get_json()
    previous_password = data['previous_password']
    new_password = data['new_password']

    if current_user.compare_hashed_password(previous_password):
        current_user.user_reset_password(new_password)
        response = jsonify({'success': 'The password has been updated successfully'})
        response.status_code = 200
        return response
    else:
        return jsonify({'warning': 'Please try to remember you previous password'})


if __name__ == '__main__':
    app.run()
