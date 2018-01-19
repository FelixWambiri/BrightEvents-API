import datetime
import re
from functools import wraps

import jwt
from sqlalchemy.exc import IntegrityError

from app import create_app

app = create_app(config_name='development')
from flask import request, jsonify, abort, render_template, make_response

from app.models.event import Event
from app.models.user import User

from app.models.user_accounts import UserAccounts

# User accounts object
user_accounts = UserAccounts()


# Root endpoint
# THis is the Root endpoint that is going to display the documentation
@app.route('/', methods=['GET'])
def index():
    return render_template('documentation.html')


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(id=data['id']).first()
        except:
            return jsonify({'message': 'Token is invalid'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


# Registration route
# All fields must be filled
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username'].strip()
    email = data['email'].strip()
    password = data['password'].strip()

    # Validate these fields against being empty
    if username is None or email is None or password is None:
        abort(400)

    # Validate the length of these fields to be more than five characters
    if len(username) < 5 or len(email) < 5 or len(password) < 5:
        return jsonify({"Warning": "This fields must be more than 5 characters and not empty spaces"})

    # Validate the username against special characters and spaces
    if not re.match("^[a-zA-Z0-9_]*$", username):
        return jsonify({
            "Warning": "Invalid username.The username can contain letters, digits and underscore but no special"
                       " characters or space"})

    # Validate the email to be properly formatted
    if not re.match(r"([\w.-]+)@([\w.-]+)(\.[\w.]+$)", email):
        return jsonify({"Warning": "Please enter a valid email"})

    # Validate the password to comprised of certain characters to make it more stronger and secure
    if not re.search("[a-z]", password) or not re.search("[0-9]", password) or not re.search("[A-Z]",
                                                                                             password) or not re.search(
        "[$#@]", password):
        return jsonify({
            "Warning": "Invalid Password.The password must contain at least one lowercase character,one digit,"
                       "one upper case character and one special character"})
    if user_accounts.get_specific_user(email):
        return jsonify({"Warning": "User already exists with email address, choose another email address"})
    else:
        user_accounts.create_user(username=username, email=email, password=password)
        response = {'message': 'You have been registered successfully and can proceed to login'}
        return make_response(jsonify(response)), 201


# Login route
@app.route('/api/auth/login', methods=['POST'])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify because not all fields were entered', 401,
                             {'WWW-Authenticate': 'Basic realm-"Login required"'})
    user = user_accounts.get_specific_user(auth.username)
    if not user:
        return make_response('Could not verify because it did not find the user in the database', 401,
                             {'WWW-Authenticate': 'Basic realm-"Login required"'})
    if user.compare_hashed_password(auth.password):
        token = jwt.encode({'id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
                           app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})
    else:
        response = jsonify({"Warning": 'Invalid Credentials'})
        response.status_code = 401  # Unauthorized
        return response


# User crud operations
# Create an event
@app.route('/api/events', methods=['POST'])
@token_required
def create_events(current_user):
    data = request.get_json()
    name = data['name'].strip()
    category = data['category'].strip()
    location = data['location'].strip()
    description = data['description'].strip()

    # Validate these fields against being empty
    if name is None or category is None or location is None:
        abort(400)

    # Validate the length of these fields to be more than five characters
    if len(name) < 5 or len(category) < 5 or len(location) < 5:
        return jsonify({"Warning": "This fields must be more than 5 characters and not empty spaces"})

    # Validate the name against special characters and spaces
    if not re.match("^[a-zA-Z0-9_]*$", name):
        return jsonify({
            "Warning": "Invalid event name.The event name can contain letters, digits and underscore but no special"
                       " characters or space"})

    # Validate the category, location and owner fields to be comprised of only alphabetic characters
    if not category.isalpha() or not location.isalpha():
        return jsonify({"Warning": "Please enter a valid input"})
    try:
        event = current_user.create_event(name=name, category=category, location=location, description=description)
        response = jsonify({"Success": "Event created successfully",
                            "event": {"name": event.name, "category": event.category, "location": event.location,
                                      "description": event.description}})
        response.status_code = 201  # Created
        return response
    except AttributeError:
        return jsonify({"Warning": 'The event already exists'})


# Update an Event
@app.route('/api/events/<string:name>', methods=['PUT'])
@token_required
def update_events(current_user, name):
    data = request.get_json()
    new_name = data['new_name']
    category = data['category']
    location = data['location']
    description = data['description']

    try:
        event = current_user.update_event(name, new_name=new_name, category=category, location=location,
                                          description=description)
        return jsonify({'success': 'The event has been updated successfully',
                        "event": {"name": event.name, "category": event.category, "location": event.location,
                                  "description": event.description}})
    except AttributeError:
        response = jsonify({'warning': 'The event does not exist'})
        response.status_code = 404  # Not found
        return response


# Delete an event from both the personal events list and the public events list"
@app.route('/api/events/<string:event_name>', methods=['DELETE'])
@token_required
def delete_events(current_user, event_name):
    try:
        current_user.delete_event(event_name)
        response = jsonify({"Success": "Event deleted successfully"})
        response.status_code = 200
        return response
    except AttributeError:
        response = jsonify({'warning': 'The event does not exist'})
        response.status_code = 404  # Not found
        return response


# Retrieves an individual event
@app.route('/api/events/<event_name>', methods=['GET'])
@token_required
def get_a_specific_event(current_user, event_name):
    if current_user.get_number_of_events() > 0:
        try:
            event = current_user.get_specific_event(event_name)
            return jsonify({"event": {"name": event.name, "category": event.category, "location": event.location,
                                      "description": event.description}})
        except AttributeError:
            response = jsonify({'warning': 'There is no such event'})
            response.status_code = 404  # Not found
            return response
    else:
        return jsonify({'Info': "No event created so far"})


# Route to display all events
@app.route('/api/events', methods=['GET'])
@token_required
def get_an_individuals_all_events(current_user):
    if current_user.get_number_of_events() > 0:
        events = Event.query.filter_by(owner=current_user.id).all()
        output = []
        for event in events:
            event_data = {'name': event.name, 'category': event.category, 'location': event.location,
                          'description': event.description}
            output.append(event_data)
        return jsonify({'events': output})
    return jsonify({'Message': 'So far you have not created any events'})


# Route to rsvp to an event
@app.route('/api/event/<name>/rsvp', methods=['GET', 'POST'])
@token_required
def rsvp_event(current_user, name):
    if request.method == 'POST':
        event = Event.query.filter_by(name=name).first_or_404
        if event:
            try:
                event.make_rsvp(current_user)
                return jsonify({'success': 'You have made a reservation successfully'}), 201
            except IntegrityError:
                return jsonify({'warning': 'You cannot make a reservation twice'}), 302
        return jsonify({'warning': 'The event you are trying to make a reservation to does not exist'})
    else:
        event = Event.query.filter_by(name=name).filter_by(owner=current_user.id).first_or_404
        if event:
            event_rsvps = event.rsvps.query.all
            if event_rsvps:
                reservations = []
                for user in event_rsvps:
                    user_data = {'username': user.username, 'email': user.email}
                    reservations.append(user_data)
                return jsonify({'Attendants': reservations})
            return jsonify({"Message": "No reservations have been made to this event yet"})
        return jsonify({'Warning': 'The event you are searching for does not exist'})


@app.route('/api/event/search_by_loc/<location>', methods=['GET'])
@token_required
def search_by_location(current_user, location):
    events_returned = current_user.search_event_by_location(location)
    events = []
    if events_returned:
        for event in events_returned:
            event_data = {'name': event.name, 'category': event.category, 'description': event.description}
            events.append(event_data)
        return jsonify({'Events found in this location': events}), 200

    return jsonify({'message': 'There are no events that have been organized here so far'})


@app.route('/api/event/search_by_cat/<category>', methods=['GET'])
@token_required
def search_by_category(current_user, category):
    events_returned = current_user.search_event_by_category(category)
    events = []
    if events_returned:
        for event in events_returned:
            event_data = {'name': event.name, 'category': event.category, 'description': event.description}
            events.append(event_data)
        return jsonify({'Events found in this category': events}), 200

    return jsonify({'message': 'There are no events that have been organized here so far'})


# Route to reset password
@app.route('/api/auth/reset-password', methods=['POST'])
@token_required
def reset_password(current_user):
    data = request.get_json()
    previous_password = data['previous_password']
    new_password = data['new_password'].strip()

    if len(new_password) < 5:
        return jsonify({"Warning": "This fields must be more than 5 characters and not empty spaces"})

    if current_user.compare_hashed_password(previous_password):
        current_user.user_reset_password(new_password)
        response = jsonify({'success': 'The password has been updated successfully'})
        response.status_code = 200
        return response
    else:
        return jsonify({'warning': 'Please try to remember you previous password'})


if __name__ == '__main__':
    app.run()
