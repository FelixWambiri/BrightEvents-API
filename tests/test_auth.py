import unittest
import json
from base64 import b64encode

from app import create_app, db


class AuthTestCase(unittest.TestCase):
    """Test case for user authentication."""

    def setUp(self):
        """Set up reusable test variables."""
        self.app = create_app(config_name='testing')
        self.user_data = json.dumps(
            {
                'username': 'Feloh',
                'email': 'felo@gmail.com',
                'password': 'FelixWambiri12@3'
            }
        )
        self.headers = {
            'Authorization': 'Basic %s' %
                             b64encode(b"felo@gmail.com:FelixWambiri12@3")
                                 .decode("ascii")}
        with self.app.app_context():
            self.client = self.app.test_client()
            db.session.close()
            db.drop_all()
            db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        del self.client

    def test_registration(self):
        """Test whether user registration works correctly."""
        res = self.client.post('/api/auth/register', data=self.user_data, content_type='application/json')
        result = json.loads(res.data.decode())
        self.assertEqual(result['message'], 'You have been registered successfully and can proceed to login')
        self.assertEqual(res.status_code, 201)

    def test_cannot_register_twice(self):
        """Test that a user cannot be registered twice."""
        res = self.client.post('/api/auth/register', data=self.user_data, content_type='application/json')
        self.assertEqual(res.status_code, 201)
        second_res = self.client.post('/api/auth/register', data=self.user_data, content_type='application/json')
        self.assertEqual(second_res.status_code, 202)
        result = json.loads(second_res.data.decode())
        self.assertEqual(
            result['Warning'], "User already exists with email address, choose another email address")

    def test_cannot_register_with_empty_spaces_in_fields(self):
        res = self.client.post("/api/auth/register",
                               data=json.dumps({"username": "Feloh",
                                                "email": "felo@gmail.com",
                                                "password": "       ",
                                                }),
                               content_type='application/json')
        """
        Test if empty spaces are passed the service returns a warning
        """
        result = json.loads(res.data.decode())
        self.assertEqual(
            result['Warning'], 'This fields must be more than 5 characters and not empty spaces')

    def test_cannot_register_with_short_fields(self):
        res = self.client.post("/api/auth/register",
                               data=json.dumps({"username": "Fel",
                                                "email": "felo@gmail.com",
                                                "password": "FelixWambiri12@3",
                                                }),
                               content_type='application/json')
        """
        Test if short data is passed the service returns a warning
        """
        result = json.loads(res.data.decode())
        self.assertEqual(
            result['Warning'], 'This fields must be more than 5 characters and not empty spaces')

    def test_cannot_register_with_invalid_email(self):
        res = self.client.post("/api/auth/register",
                               data=json.dumps({"username": "Felix",
                                                "email": "felogmailcom",
                                                "password": "FelixWambiri12@3",
                                                }),
                               content_type='application/json')
        """
        Test if invalid data are passed the service returns a warning
        """
        result = json.loads(res.data.decode())
        self.assertEqual(
            result['Warning'], 'Please enter a valid email')

    def test_login(self):
        self.client.post('/api/auth/register', data=self.user_data, content_type='application/json')
        res_1 = self.client.post("/api/auth/login", headers=self.headers, content_type='application/json')
        self.assertIn(b'token', res_1.data)

    def test_cannot_login_without_registration(self):
        res_1 = self.client.post("/api/auth/login", headers=self.headers, content_type='application/json')
        self.assertIn(b'Could not verify because it did not find the user in the database', res_1.data)

    def test_invalid_login_credentials_raises_error(self):
        self.client.post('/api/auth/register', data=self.user_data, content_type='application/json')
        res_1 = self.client.post("/api/auth/login", headers={
            'Authorization': 'Basic %s' %
                             b64encode(b"felo@gmail.com:FelixWambiri12@3456")
                                 .decode("ascii")}, content_type='application/json')
        self.assertIn(b'Invalid Credentials', res_1.data)
