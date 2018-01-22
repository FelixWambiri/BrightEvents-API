import datetime
import re
from functools import wraps

from flask import request, jsonify, abort, render_template, make_response
import jwt

from app.models.user import User
from . import auth
from app.models.user_accounts import UserAccounts
from app.instance.config import BaseConfig


# User accounts object
user_accounts = UserAccounts()


# Root endpoint
# THis is the Root endpoint that is going to display the documentation
@auth.route('/', methods=['GET'])
def index():
    return render_template('documentation.html')


# Registration route
# All fields must be filled
@auth.route('/register', methods=['POST'])
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
        return jsonify({"Warning": "User already exists with email address, choose another email address"}), 202
    else:
        user_accounts.create_user(username=username, email=email, password=password)
        response = {'message': 'You have been registered successfully and can proceed to login'}
        return make_response(jsonify(response)), 201


# Login route
@auth.route('/login', methods=['POST'])
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
                           BaseConfig.SECRET_KEY)
        return jsonify({'token': token.decode('UTF-8')}), 200
    else:
        response = jsonify({"Warning": 'Invalid Credentials'})
        response.status_code = 401  # Unauthorized
        return response


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            data = jwt.decode(token, BaseConfig.SECRET_KEY)
            current_user = User.query.filter_by(id=data['id']).first()
        except:
            return jsonify({'message': 'Token is invalid'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


# Route to reset password
@auth.route('/reset-password', methods=['POST'])
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
