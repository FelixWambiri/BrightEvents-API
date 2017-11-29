from flask import Flask, request, jsonify, abort

from app.models.user import User
from app.models.user_accounts import UserAccounts

app = Flask(__name__)

# Import the apps configuration settings from config file in instance folder
app.config.from_object('app.instance.config.DevelopmentConfig')

# User accounts object
user_accounts = UserAccounts()


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


if __name__ == '__main__':
    app.run()
