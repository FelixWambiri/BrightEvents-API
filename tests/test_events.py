import unittest
from base64 import b64encode

from flask import json

from app import create_app, db


class EventTestCase(unittest.TestCase):
    """ This class represents the Bright Events test cases """

    def setUp(self):
        """ Set up reusable test variables. """

        self.app = create_app(config_name='testing')
        self.app.app_context().push()
        # Define events details that will be used in the different methods
        self.event1_data = json.dumps(
            {
                'name': 'Bootcamp',
                'category': 'Learning',
                'location': 'Nairobi',
                'date_hosted': '8-8-2018',
                'description': 'This is the best learning experience'
            }
        )
        self.event2_data = json.dumps(
            {
                'name': 'Bootcamp_21',
                'category': 'Learning',
                'location': 'Uganda',
                'date_hosted': '8-8-2018',
                'description': 'This is the best learning experience'
            }
        )
        self.event3_data = json.dumps(
            {
                'name': 'Sepetuka',
                'category': 'social',
                'location': 'mombasa',
                'date_hosted': '8-8-2018',
                'description': 'This is the best social experience'
            }
        )
        self.event4_data = json.dumps(
            {
                'name': 'Blaze',
                'category': 'Cooporate',
                'location': 'Nakuru',
                'date_hosted': '8-8-2018',
                'description': 'This is the best corporate experience'
            }
        )
        self.user1_data = json.dumps(
            {
                'username': 'Felix',
                'email': 'felix@gmail.com',
                'password': 'FelixWambiri12@3'
            }
        )
        self.user2_data = json.dumps(
            {
                'username': 'Testcase',
                'email': 'test@gmail.com',
                'password': 'TestCase12@3'
            }

        )
        self.user3_data = json.dumps(
            {
                'username': 'Testcase1',
                'email': 'test1@gmail.com',
                'password': 'TestCase12@3'
            })
        # Define a persons` login details that is the username and the password
        self.headers1 = {
            'Authorization': 'Basic %s' %
                             b64encode(b"felix@gmail.com:FelixWambiri12@3")
                             .decode("ascii")}
        self.headers2 = {
            'Authorization': 'Basic %s' %
                             b64encode(b"test@gmail.com:TestCase12@3")
                             .decode("ascii")}
        self.headers5 = {
            'Authorization': 'Basic %s' %
                             b64encode(b"test1@gmail.com:TestCase12@3")
                             .decode("ascii")}

        with self.app.app_context():
            self.client = self.app.test_client()
            db.session.close()
            db.drop_all()
            db.create_all()

    # Register and login the above defined people instead of doing so in each method
    def register_user1(self):
        return self.client.post('/api/auth/register', data=self.user1_data, content_type='application/json')

    def login_user1(self):
        return self.client.post("/api/auth/login", headers=self.headers1, content_type='application/json')

    def register_user2(self):
        return self.client.post('/api/auth/register', data=self.user2_data, content_type='application/json')

    def login_user2(self):
        return self.client.post("/api/auth/login", headers=self.headers2, content_type='application/json')

    def register_user3(self):
        return self.client.post('/api/auth/register', data=self.user3_data, content_type='application/json')

    def login_user3(self):
        return self.client.post("/api/auth/login", headers=self.headers5, content_type='application/json')

    def test_that_without_token_based_authentication_you_cannot_perform_any_CRUD_operation(self):
        """
        Test that you cannot perform any CRUD operation without having a valid token.
        Each operation requires token authentication
        :return:
        """
        self.register_user1()
        result = self.login_user1()
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # Test creating an event but no token is passed
        # A Token is missing error is returned
        res = self.client.post('/api/events', data=self.event3_data, content_type='application/json')
        self.assertIn(b'Token is missing"', res.data)

        # Create an actual event to be used in testing other operations by passing in the token
        res = self.client.post('/api/events', headers=headers3, data=self.event4_data, content_type='application/json')
        self.assertEqual(res.status_code, 201)

        # Test updating an event but no token is passed
        # A Token is missing error is returned
        res_1 = self.client.put('/api/events/1', data=json.dumps(
            {
                'name': 'Bootcamp',
                'new_name': 'Bootcamp_Uganda',
                'category': 'Learning',
                'location': 'Uganda',
                'date_hosted': '8-8-2018',
                'description': 'This is the best learning experience'
            }
        ), content_type='application/json')
        self.assertIn(b'Token is missing', res_1.data)

        # Test deleting an event but no token is passed
        # A Token is missing error is returned
        res = self.client.delete('/api/events/1')
        self.assertIn(b'Token is missing', res.data)

        # Test getting one specific event but no token
        # A Token is missing error is returned
        res_z = self.client.get('/api/event/1')
        self.assertIn(b'Token is missing', res_z.data)

        # Test getting all individual events without passing a token
        # A Token is missing error is returned
        result = self.client.get('/api/my_events')
        self.assertIn(b'Token is missing', result.data)

    def test_successful_event_creation(self):
        """Test successful event creation by passing the required attributes and a valid token"""
        # Register a user
        self.register_user1()
        # Login the user
        result = self.login_user1()
        # Get the token generated
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}
        res = self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')
        self.assertEqual(res.status_code, 201)

    def test_successful_multiple_event_creation_by_single_user(self):
        """Test that a user can create multiple events"""
        # Register a user
        self.register_user1()
        # Login the user
        result = self.login_user1()
        # Get the token generated
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # User creates the first evnt
        res = self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')
        self.assertEqual(res.status_code, 201)

        # User creates the second event
        res = self.client.post('/api/events', headers=headers3, data=self.event2_data, content_type='application/json')
        self.assertEqual(res.status_code, 201)

        # User creates the third event
        res = self.client.post('/api/events', headers=headers3, data=self.event3_data, content_type='application/json')
        self.assertEqual(res.status_code, 201)

    def test_unsuccessful_creation_of_duplicate_events(self):
        """
        Test that the user cannot create the same exact event twice
        Meaning that the user cannot create two events containing the same exact details
        """
        # Register a user
        self.register_user1()
        # Login the user
        result = self.login_user1()
        # Get the token generated
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # Create the event the first time
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')

        # Try to create the same event the second time
        # An event already exists error is raised
        result = self.client.post('/api/events', headers=headers3, data=self.event1_data,
                                  content_type='application/json')
        self.assertIn(b'The event already exists', result.data)

    def test_unsuccessful_creation_of_events_when_invalid_details_used(self):
        """
        Test that for you to create an event successfully you have to pass in valid data details
        :return:
        """
        # Register a user
        self.register_user1()
        # Login the user
        result = self.login_user1()
        # Get the token generated
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # Try creating an event with a name with less than five characters and you will get an error
        res = self.client.post('/api/events', headers=headers3, data=json.dumps(
            {
                'name': 'B',
                'category': 'Learning',
                'location': 'Nairobi',
                'date_hosted': '8-8-2018',
                'description': 'This is the best learning experience'
            }
        ), content_type='application/json')
        self.assertIn(b'an underscore and be at least 5 characters in length without any empty spaces', res.data)

        # Try creating an event with a name that contains special characters and you will get an error
        res = self.client.post('/api/events', headers=headers3, data=json.dumps(
            {
                'name': 'Bootcamp# nbo$',
                'category': 'Learning',
                'location': 'Nairobi',
                'date_hosted': '8-8-2018',
                'description': 'This is the best learning experience'
            }
        ), content_type='application/json')
        self.assertIn(b'The event name should only contain alphanumeric characters,an underscore', res.data)

        # Try creating an event with a Location and category field containing numeric characters and you will
        #  get an error
        res = self.client.post('/api/events', headers=headers3, data=json.dumps(
            {
                'name': 'Bootcamp',
                'category': 'Learning123',
                'location': 'Nairobi',
                'date_hosted': '8-8-2018',
                'description': 'This is the best learning experience'
            }
        ), content_type='application/json')
        self.assertIn(b'The event category should only contain alphabetic characters', res.data)

    def test_successful_event_update(self):
        """
        Test that a user can update an event successfully provided that it is the user who created the event
        :return:
        """
        # Register a user
        self.register_user1()
        # Login the user
        result = self.login_user1()
        # Get the token generated
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # The User creates the event
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')

        # The user is able to update the event successfully
        res_1 = self.client.put('/api/events/1', headers=headers3, data=json.dumps(
            {
                'name': 'BootCamp Uganda',
                'category': 'Learning',
                'location': 'Uganda',
                'date_hosted': '8-8-2018',
                'description': 'This is the best learning experience'
            }
        ), content_type='application/json')
        self.assertIn(b'BootCamp Uganda', res_1.data)
        self.assertEqual(res_1.status_code, 200)

    def test_that_fields_are_optional_when_updating(self):
        """
        Test that it is not compulsory for the User to update all the fields.They are optional to update and the
        previous field details is populated back.
        :return:
        """
        # Register a user
        self.register_user1()
        # Login the user
        result = self.login_user1()
        # Get the token generated
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # User creates the event
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')

        # User updates the event but leaves some fields empty
        res_1 = self.client.put('/api/events/1', headers=headers3, data=json.dumps(
            {
                'name': 'Self Learning clinic',
                'category': '',
                'location': 'Nairobi',
                'date_hosted': '8-8-2018',
                'description': ''
            }
        ), content_type='application/json')
        # Confirm that the description field is populated back with the previous data
        self.assertIn(b'This is the best learning experience', res_1.data)
        self.assertEqual(res_1.status_code, 200)

    def test_unsuccessful_update_of_event_not_created_by_current_user(self):
        """
        Test that a user cannot update an event that they did not create
        :return:
        """
        # Register user one
        self.register_user1()
        # Login user one
        result = self.login_user1()
        # Get the token generated for user one
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # User one creates the first event
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')

        # Register user two
        self.register_user2()
        # Login user two
        result = self.login_user2()
        # Get the token generated for user two
        access_token2 = json.loads(result.data.decode())['token']
        headers4 = {'x-access-token': access_token2}

        # User two creates the second event
        res = self.client.post('/api/events', headers=headers4, data=self.event3_data, content_type='application/json')
        self.assertEqual(res.status_code, 201)

        # User two tries to update the first event created by user One.
        # Tries to update an event that they did not create
        res_1 = self.client.put('/api/events/1', headers=headers4, data=json.dumps(
            {
                'name': 'BootCamp Uganda',
                'category': 'Learning',
                'location': 'Uganda',
                'date_hosted': '8-8-2018',
                'description': 'This is the best learning experience'
            }
        ), content_type='application/json')
        # The user gets a notification that the event they are trying to update does not exist because it is not the
        #  user who created it
        self.assertIn(b'The event does not exist', res_1.data)

    def test_unsuccessful_update_of_a_non_existent_event(self):
        """
        Test that the user cannot update an event that does not exist
        :return:
        """
        # Register the user
        self.register_user1()
        # login the user
        result = self.login_user1()
        # Get the token generated
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        res_1 = self.client.put('/api/events/14', headers=headers3, data=json.dumps(
            {
                'name': 'BootCamp Uganda',
                'category': 'Learning',
                'location': 'Uganda',
                'date_hosted': '8-8-2018',
                'description': 'This is the best learning experience'
            }
        ), content_type='application/json')
        self.assertIn(b'The event does not exist', res_1.data)

    def test_successful_deletion_of_an_event(self):
        """
        Test that a user can delete an event successfully provided they are the one who created the event
        :return:
        """
        # Register the user
        self.register_user1()
        # login the user
        result = self.login_user1()
        # Get the token generated
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # The user creates the event
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')

        # The user deletes event successfully
        res = self.client.delete('/api/events/1', headers=headers3)
        self.assertIn(b'Event deleted successfully', res.data)
        self.assertEqual(res.status_code, 200)

    def test_unsuccessful_deletion_of_event_not_created_by_current_user(self):
        """
        Test that the user cannot delete an event that they did not create
        :return:
        """
        # Register the user
        self.register_user1()
        # login the user
        result = self.login_user1()
        # Get the token generated
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # User one creates the first event
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')

        # Register user two
        self.register_user2()
        # login user two
        result = self.login_user2()
        access_token2 = json.loads(result.data.decode())['token']
        headers4 = {'x-access-token': access_token2}

        # User two tries to delete an event created by user one
        # An event does not exist error is returned
        res_1 = self.client.delete('/api/events/1', headers=headers4)
        self.assertIn(b'The event does not exist', res_1.data)

    def test_unsuccessful_deletion_of_a_non_existent_event(self):
        """
        Test that a user cannot delete an event that does not exist
        :return:
        """
        # Register user
        self.register_user1()
        # login user
        result = self.login_user1()
        # Get the token generated
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # The user tries to delete an event that does not exist
        # An event does not exist error is raised
        res_1 = self.client.delete('/api/events/12', headers=headers3)
        self.assertIn(b'The event does not exist', res_1.data)

        # The user creates the event
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')

        # The user deletes the event
        res = self.client.delete('/api/events/1', headers=headers3)
        self.assertIn(b'Event deleted successfully', res.data)
        self.assertEqual(res.status_code, 200)

        # The user tries to delete the event deleted above the second time
        # An event does not exist error is returned
        # This test proves that an event is deleted permanently from the database
        res = self.client.delete('/api/events/1', headers=headers3)
        self.assertIn(b'The event does not exist', res.data)

    def test_successful_retrieval_of_event_created_by_current_user(self):
        """
        Test that a user can retrieve a specific event provided they are the one who created the event
        :return:
        """
        # Register user
        self.register_user1()
        # login user
        result = self.login_user1()
        # Get the token generated
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # The user creates the first event
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')

        # The user creates the second event
        self.client.post('/api/events', headers=headers3, data=self.event2_data, content_type='application/json')

        # The User retrieves the first event
        res_z = self.client.get('/api/event/1', headers=headers3)
        self.assertIn(b'Bootcamp', res_z.data)

    def test_unsuccessful_retrieval_of_event_not_created_by_current_user(self):
        """
        Test that a user cannot retrieve an event that they have not created
        :return:
        """
        # Register user
        self.register_user1()
        # login user
        result = self.login_user1()
        # Get the token generated
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # Register user two
        self.register_user2()
        # login user two
        result = self.login_user2()
        # Get the token generated for user two
        access_token2 = json.loads(result.data.decode())['token']
        headers4 = {'x-access-token': access_token2}

        # User one creates the first event
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')

        # User two tries to retrieve an event created by user one and gets a No Events Found error message
        res_z = self.client.get('/api/event/3', headers=headers4)
        self.assertIn(b'No Events Found', res_z.data)

    def test_successful_retrieval_of_ones_overall_events(self):
        """
        Test that a user can get all their individual events
        :return:
        """
        # Register user
        self.register_user1()
        # login user
        result = self.login_user1()
        # Get the token generated
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # The user creates the first event
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')

        # The user creates the second event
        self.client.post('/api/events', headers=headers3, data=self.event2_data, content_type='application/json')

        # The user creates the third event
        self.client.post('/api/events', headers=headers3, data=self.event3_data, content_type='application/json')

        # The user retrieves all their events and the sum up to the actual three events created
        result = self.client.get('/api/my_events', headers=headers3)
        events = json.loads(result.data.decode())['events']
        self.assertEqual(3, len(events))

    def test_unsuccessful_retrieval_of_events_not_created_by_current_user(self):
        """
        Test that a user cannot be able to get another users`s events
        :return:
        """
        # Register user
        self.register_user1()
        # login user
        result = self.login_user1()
        # Get the token generated
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # User one creates the first event
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')

        # User one creates the second event
        self.client.post('/api/events', headers=headers3, data=self.event2_data, content_type='application/json')

        # Register user two
        self.register_user2()
        # login user two
        result = self.login_user2()
        # Get the token generated by user two
        access_token2 = json.loads(result.data.decode())['token']
        headers4 = {'x-access-token': access_token2}

        # User two creates their first event
        self.client.post('/api/events', headers=headers4, data=self.event3_data, content_type='application/json')

        # User two creates their second event
        self.client.post('/api/events', headers=headers4, data=self.event4_data, content_type='application/json')

        # Test to see that two events are returned for user one
        result = self.client.get('/api/my_events', headers=headers3)
        events1 = json.loads(result.data.decode())['events']
        self.assertEqual(2, len(events1))

        # Test to see that two events are returned for user one
        result = self.client.get('/api/my_events', headers=headers4)
        events2 = json.loads(result.data.decode())['events']
        self.assertEqual(2, len(events2))

    def test_successful_retrieval_of_all_events(self):
        """
        Test that a user can see/get all the events in the database
        :return:
        """
        # Register user
        self.register_user1()
        # login user
        result = self.login_user1()
        # Get the token generated
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # User one creates the first event
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')

        # User one creates the second event
        self.client.post('/api/events', headers=headers3, data=self.event2_data, content_type='application/json')

        # User one creates the third event
        self.client.post('/api/events', headers=headers3, data=self.event3_data, content_type='application/json')

        # Register user two
        self.register_user2()
        # login user two
        result = self.login_user2()
        # Get the token generated for user two
        access_token2 = json.loads(result.data.decode())['token']
        headers4 = {'x-access-token': access_token2}

        # User two creates the fourth event
        self.client.post('/api/events', headers=headers4, data=self.event4_data, content_type='application/json')

        # User gets all the events
        result = self.client.get('/api/events')
        events = json.loads(result.data.decode())['events']
        self.assertEqual(4, len(events))

    def test_making_reservations_to_an_event_successfully(self):
        """
        Test making a successful reservation to an event
        :return:
        """
        # Register user
        self.register_user1()
        # login user
        result = self.login_user1()
        # Get the token generated
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # Register user two
        self.register_user2()
        # login user two
        result = self.login_user2()
        # Get the token generated for user two
        access_token2 = json.loads(result.data.decode())['token']
        headers4 = {'x-access-token': access_token2}

        # User one creates the first event
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')
        # User two successfully makes a reservation to user event created by user one
        result = self.client.post('/api/event/1/rsvp', headers=headers4)
        self.assertIn(b'You have made a reservation successfully', result.data)

    def test_unsuccessful_reservations_to_an_event_twice(self):
        """
        Test that it is not possible for the same user to make a reservation to the same event twice
        :return:
        """
        # Register user
        self.register_user1()
        # login user
        result = self.login_user1()
        # Get the token generated
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # Register user two
        self.register_user2()
        # login user two
        result = self.login_user2()
        # Get the token generated for user two
        access_token2 = json.loads(result.data.decode())['token']
        headers4 = {'x-access-token': access_token2}

        # User one creates the first event
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')
        # User two successfully makes a reservation to user event created by user one
        result = self.client.post('/api/event/1/rsvp', headers=headers4)
        self.assertIn(b'You have made a reservation successfully', result.data)

        # User two tries to make a reservation to the same event the second time
        result = self.client.post('/api/event/1/rsvp', headers=headers4)
        self.assertIn(b'You cannot make a reservation twice', result.data)

    def test_successful_return_of_all_the_reservations(self):
        """
        Test that a user can see other users who have made a reservation to their event
        :return:
        """
        # Register user
        self.register_user1()
        # login user
        result = self.login_user1()
        # Get the token generated
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # Register user two
        self.register_user2()
        # login user two
        result = self.login_user2()
        # Get the token generated for user two
        access_token2 = json.loads(result.data.decode())['token']
        headers4 = {'x-access-token': access_token2}

        # Register user three
        self.register_user3()
        # login user three
        result = self.login_user3()
        # Get the token generated for user three
        access_token3 = json.loads(result.data.decode())['token']
        headers6 = {'x-access-token': access_token3}

        # User one creates event the first event
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')

        # User two makes a reservation o the event created by user one
        self.client.post('/api/event/1/rsvp', headers=headers4)

        # User three makes a reservation o the event created by user one
        self.client.post('/api/event/1/rsvp', headers=headers6)

        # Show the number of users who have made reservations to the event created by user one
        result = self.client.get('/api/event/1/rsvp', headers=headers3)
        events = json.loads(result.data.decode())['Attendants']
        self.assertEqual(2, len(events))

    def test_unsuccessful_access_to_reservations_not_created_by_current_user(self):
        """
        Test that a user cannot see reservations made to an event they did not create
        :return: Reservations mae to an event
        """
        # Register user
        self.register_user1()
        # login user
        result = self.login_user1()
        # Get the token generated
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # Register user two
        self.register_user2()
        # login user two
        result = self.login_user2()
        # Get the token generated for user two
        access_token2 = json.loads(result.data.decode())['token']
        headers4 = {'x-access-token': access_token2}

        # Register user three
        self.register_user3()
        # login user three
        result = self.login_user3()
        # Get the token generated for user three
        access_token3 = json.loads(result.data.decode())['token']
        headers6 = {'x-access-token': access_token3}

        # User one creates event the first event
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')

        # User two makes a reservation o the event created by user one
        self.client.post('/api/event/1/rsvp', headers=headers4)

        # User three makes a reservation o the event created by user one
        self.client.post('/api/event/1/rsvp', headers=headers6)

        # User three tries to see reservations made belonging an event created by user one and they get an error
        result = self.client.get('/api/event/1/rsvp', headers=headers4)
        self.assertEqual(result.status_code, 401)

    def test_successful_event_searching_by_location(self):
        """
        Test that a user can successfully search for a given event by location
        :return:
        """
        # Register user
        self.register_user1()
        # login user
        result = self.login_user1()
        # Get the token generated
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # Register user two
        self.register_user2()
        # login user two
        result = self.login_user2()
        # Get the token generated for user two
        access_token2 = json.loads(result.data.decode())['token']
        headers4 = {'x-access-token': access_token2}

        # User creates an event in Nairobi
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')

        # User creates an event in Uganda
        self.client.post('/api/events', headers=headers3, data=self.event2_data, content_type='application/json')

        # User creates an event in Mombasa
        self.client.post('/api/events', headers=headers3, data=self.event3_data, content_type='application/json')

        # User searches for an event whose location is in Uganda
        result = self.client.post('/api/search', headers=headers4, data=json.dumps({'location': 'Uganda'}),
                                  content_type='application/json')

        # User finds the event held in Mombasa
        events = json.loads(result.data.decode())['Events found in this location']
        self.assertEqual(1, len(events))

        """
        Test that no event is returned if no event exists with the given location in the search parameter
        """
        result1 = self.client.post('/api/search', headers=headers4, data=json.dumps({'location': 'Kisumu'}),
                                   content_type='application/json')
        self.assertIn(b'No Events Found', result1.data)

    def test_successful_event_searching_by_category(self):
        """
               Test that a user can successfully search for a given event by location
               :return:
        """
        # Register user
        self.register_user1()
        # login user
        result = self.login_user1()
        # Get the token generated
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # Register user two
        self.register_user2()
        # login user two
        result = self.login_user2()
        # Get the token generated for user two
        access_token2 = json.loads(result.data.decode())['token']
        headers4 = {'x-access-token': access_token2}

        # User creates an event with Learning as the category
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')

        # User creates another event with Learning as the category
        self.client.post('/api/events', headers=headers3, data=self.event2_data, content_type='application/json')

        # User creates an event with Social being the category
        self.client.post('/api/events', headers=headers3, data=self.event3_data, content_type='application/json')

        # User searches and finds the events that have learning as their category
        result = self.client.post('/api/search', headers=headers4, data=json.dumps({'category': 'learning'}),
                                  content_type='application/json')
        events = json.loads(result.data.decode())['Events belonging to this category']
        self.assertEqual(2, len(events))

        """
        Test that no event is returned if no event exists with the category given in the search parameter
        """
        result1 = self.client.post('/api/search', headers=headers4, data=json.dumps({'category': 'Adventure'}),
                                   content_type='application/json')
        self.assertIn(b'No Events Found', result1.data)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        del self.client


if __name__ == '__main__':
    unittest.main()
