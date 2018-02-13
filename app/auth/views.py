import datetime
import re
import socket
from functools import wraps
from threading import Thread

import os
from flask import request, jsonify, abort, render_template, make_response, current_app
import jwt
from flask_mail import Message

from app import mail, db
from app.models.user import User, BlacklistToken
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


def password_validation(data):
    if len(data['new_pass'].strip()) < 5 or not re.search("[a-z]", data['new_pass'].strip()) or not \
            re.search("[0-9]", data['new_pass'].strip()) or not re.search("[A-Z]", data['new_pass'].strip()) \
            or not re.search("[$#@]", data['new_pass'].strip()):
        return "Invalid Password.The password must contain at least one lowercase character,one digit,one upper " \
               "case character and one special character"
    else:
        return data['new_pass']


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(subject, sender=os.environ.get('MAIL_USERNAME'), recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


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


@auth.route('/acquire_token', methods=['POST'])
def acquire_token():
    """
    Method generates the confirmation token for password reset and sends that email to the user email
    :return:
    """
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user:
        token = user.generate_confirmation_token()
        try:
            send_email(user.email, 'Confirm Your Account', 'auth/email/confirm', user=user, token=token)
            response = {"message": "a confirmation email has been sent to {}".format(user.email)}
            return make_response(jsonify(response)), 200
        except socket.gaierror:
            return jsonify({'Error': 'Sorry an error has been encountered while sending you a confirmation link.'
                                     'Check your internet connection first it may be the reason'})
    return jsonify({"Info": "There does not exist a user by that email address"}), 404


@auth.route('/confirm/<token>')
def confirm(token):
    """This route contains the token that will be used to reset password"""
    res = User.confirm(token)
    if res == False:
        return jsonify({"message": res}), 403
    return jsonify({"message": "Extract the token below and go ahead to reset your password", "token": token}), 200


@auth.route('/reset_password', methods=['PUT'])
def reset_password():
    """
    This route resets the password and takes the token received in rhe email and the new password
    :return:
    """
    data = request.get_json()
    try:
        token = data['token']
    except KeyError:
        return jsonify({"Info": "Please input the token received in your email and your new password"}),
    res = User.confirm(token)
    if res == False:
        return jsonify({"message": res}), 403
    user = res
    new_pass = password_validation(data)

    if new_pass is not data['new_pass']:
        return jsonify({"message": new_pass}), 400
    user.pw_hash = data["new_pass"]
    db.session.commit()
    return jsonify({"message": "The password was reset successfully,Now you can proceed to login"}), 200


# Route to change password
@auth.route('/change-password', methods=['PUT'])
@token_required
def change_password(current_user):
    """
    This route changes the password
    :param current_user:
    :return:
    """
    data = request.get_json()
    previous_password = data['previous_password']
    new_pass = password_validation(data)
    if new_pass is not data['new_pass']:
        return jsonify({"message": new_pass}), 400

    if current_user.compare_hashed_password(previous_password):
        current_user.change_password(new_pass)
        response = jsonify({'success': 'The password has been updated successfully'})
        response.status_code = 200
        return response
    else:
        return jsonify({'warning': 'Please try to remember you previous password'})


# Route to logout
@auth.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    token = request.headers.get('x-access-token')
    if token:
        data = jwt.decode(token, BaseConfig.SECRET_KEY)
        if not isinstance(data, str) and not BlacklistToken.check_blacklist(token):
            # mark the token as blacklisted
            blacklist_token = BlacklistToken(token=token)
            try:
                # insert the token
                db.session.add(blacklist_token)
                db.session.commit()
                return jsonify({'status': 'success', 'message': 'Successfully logged out.'}), 200
            except Exception as e:
                return jsonify({'status': 'fail', 'message': e}), 200
        else:
            return jsonify({'status': 'fail', 'message': data}), 401
    else:
        return jsonify({'status': 'fail', 'message': 'Provide a valid token.'}), 403
