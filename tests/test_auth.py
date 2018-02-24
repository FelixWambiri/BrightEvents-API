import unittest
import json
from base64 import b64encode

from app import create_app, db
from app.models.user import User


class AuthTestCase(unittest.TestCase):
    """ Test case for user authentication. """

    def setUp(self):
        """ Set up reusable test variables. """
        self.app = create_app(config_name='testing')
        self.app.app_context().push()
        # Define the details needed to register a person
        self.user_data = json.dumps(
            {
                'username': 'Feloh',
                'email': 'felo@gmail.com',
                'password': 'FelixWambiri12@3'
            }
        )
        self.user_data2 = json.dumps(
            {
                'username': 'Felix',
                'email': 'felixwambiri@gmail.com',
                'password': 'FelixWambiri12@3'
            }
        )
        # Define the details needed to login this user
        self.headers = {
            'Authorization': 'Basic %s' %
                             b64encode(b"felo@gmail.com:FelixWambiri12@3")
                             .decode("ascii")}
        with self.app.app_context():
            self.client = self.app.test_client()
            db.session.close()
            db.drop_all()
            db.create_all()

    def test_password_setter(self):
        """
        Test that a password is set successfully when a person is created
        :return:
        """
        user = User('Felix', 'felixwambiri@gmail.com', 'FelixWambiri12@3')
        self.assertTrue(user.pw_hash is not None)

    def test_no_password_getter(self):
        """
        Test that password attribute has a write only property
        :return:
        """
        user = User('Felix', 'felixwambiri@gmail.com', 'FelixWambiri12@3')
        with self.assertRaises(AttributeError):
            user.password()

    def test_password_verification(self):
        """
        Test that the method to verify between the plain password and the hashed password works
        :return:
        """
        user = User('Felix', 'felixwambiri@gmail.com', 'FelixWambiri12@3')
        self.assertTrue(user.compare_hashed_password('FelixWambiri12@3'))
        self.assertFalse(user.compare_hashed_password('WambiriFelix12@3'))

    def test_password_salts_are_random(self):
        """
        Test that hashing of passwords is random
        :return:
        """
        user = User('Felix', 'felixwambiri@gmail.com', 'FelixWambiri12@3')
        user2 = User('Felix', 'felixwambiri@gmail.com', 'FelixWambiri12@3')
        self.assertTrue(user.pw_hash != user2.pw_hash)

    def test_successful_user_registration(self):
        """ Test whether user registration method works correctly. """
        res = self.client.post('/api/auth/register', data=self.user_data, content_type='application/json')
        result = json.loads(res.data.decode())
        self.assertEqual(result['message'], 'You have been registered successfully and can proceed to login')
        self.assertEqual(res.status_code, 201)

    def test_unsuccessful_registration_of_the_same_user_twice(self):
        """ Test that the same user cannot be registered twice. """
        self.client.post('/api/auth/register', data=self.user_data, content_type='application/json')
        second_res = self.client.post('/api/auth/register', data=self.user_data, content_type='application/json')
        self.assertEqual(second_res.status_code, 202)
        result = json.loads(second_res.data.decode())
        self.assertEqual(
            result['Warning'], "User already exists with email address, choose another email address")

    def test_unsuccessful_registration_of_a_user_using_invalid_details_with_empty_fields(self):
        res = self.client.post("/api/auth/register",
                               data=json.dumps({"username": "Feloh",
                                                "email": "felo@gmail.com",
                                                "password": "       ",
                                                }),
                               content_type='application/json')
        #  Test if empty spaces are passed the request returns a warning
        result = json.loads(res.data.decode())
        self.assertEqual(
            result['Warning'], 'This fields must be more than 5 characters and not empty spaces')

    def test_unsuccessful_registration_of_a_user_using_invalid_details_with_short_fields(self):
        res = self.client.post("/api/auth/register",
                               data=json.dumps({"username": "Fel",
                                                "email": "felo@gmail.com",
                                                "password": "FelixWambiri12@3",
                                                }),
                               content_type='application/json')
        # Test if short data is passed the request returns a warning
        result = json.loads(res.data.decode())
        self.assertEqual(
            result['Warning'], 'This fields must be more than 5 characters and not empty spaces')

    def test_unsuccessful_registration_of_a_user_using_invalid_details_with_invalid_email(self):
        res = self.client.post("/api/auth/register",
                               data=json.dumps({"username": "Felix",
                                                "email": "felogmailcom",
                                                "password": "FelixWambiri12@3",
                                                }),
                               content_type='application/json')
        # Test if invalid data are passed the service returns a warning
        result = json.loads(res.data.decode())
        self.assertEqual(
            result['Warning'], 'Please enter a valid email')

    def test_successful_user_login(self):
        self.client.post('/api/auth/register', data=self.user_data, content_type='application/json')
        res_1 = self.client.post("/api/auth/login", headers=self.headers, content_type='application/json')
        self.assertIn(b'token', res_1.data)

    def test_unsuccessful_login_without_registration(self):
        res_1 = self.client.post("/api/auth/login", headers=self.headers, content_type='application/json')
        self.assertIn(b'Could not verify because it did not find the user in the database', res_1.data)

    def test_unsuccessful_login_with_invalid_login_credentials(self):
        self.client.post('/api/auth/register', data=self.user_data, content_type='application/json')
        res_1 = self.client.post("/api/auth/login", headers={
            'Authorization': 'Basic %s' %
                             b64encode(b"felo@gmail.com:FelixWambiri12@3456")
                                 .decode("ascii")}, content_type='application/json')
        self.assertIn(b'Invalid Credentials', res_1.data)

    def test_successful_logout(self):
        """ Test for successful logout before token expiration """
        # The user is registered
        self.client.post('/api/auth/register', data=self.user_data, content_type='application/json')
        # The user is logged in
        result = self.client.post("/api/auth/login", headers=self.headers, content_type='application/json')
        access_token = json.loads(result.data.decode())['token']
        header = {'x-access-token': access_token}
        # The user is logged out successfully if the token has not yet expired
        res = self.client.post("/api/auth/logout", headers=header, content_type='application/json')
        data = json.loads(res.data.decode())
        self.assertIn("Successfully logged out", str(data))
        self.assertEqual(res.status_code, 200)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        del self.client


if __name__ == '__main__':
    unittest.main()
