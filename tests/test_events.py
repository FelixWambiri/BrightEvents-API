import unittest
from base64 import b64encode

from flask import json

from app import create_app, db


class EventTestCase(unittest.TestCase):
    """This class represents the bucketlist test case"""

    def setUp(self):
        """Set up reusable test variables."""

        self.app = create_app(config_name='testing')
        self.app.app_context().push()
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

    def test_that_without_token_based_authentication_you_cannot_perform_any_crud_operation(self):
        # create user to create events for testing other methods
        self.register_user1()
        result = self.login_user1()
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # create event but no token passed
        res = self.client.post('/api/events', data=self.event3_data, content_type='application/json')
        self.assertIn(b'Token is missing"', res.data)

        # Create event to be used in testing other methods
        res = self.client.post('/api/events', headers=headers3, data=self.event4_data, content_type='application/json')
        self.assertEqual(res.status_code, 201)

        # update  but no token passed
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

        # delete event but no token passed
        res = self.client.delete('/api/events/1')
        self.assertIn(b'Token is missing', res.data)

        # get one specific event
        res_z = self.client.get('/api/event/1')
        self.assertIn(b'Token is missing', res_z.data)

        # get all your events
        result = self.client.get('/api/my_events')
        self.assertIn(b'Token is missing', result.data)

    def test_event_creation(self):
        self.register_user1()
        result = self.login_user1()
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}
        res = self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')
        self.assertEqual(res.status_code, 201)

    def test_multiple_event_creation_by_user(self):
        self.register_user1()
        result = self.login_user1()
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # First event
        res = self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')
        self.assertEqual(res.status_code, 201)

        # second event
        res = self.client.post('/api/events', headers=headers3, data=self.event2_data, content_type='application/json')
        self.assertEqual(res.status_code, 201)

        # Third event
        res = self.client.post('/api/events', headers=headers3, data=self.event3_data, content_type='application/json')
        self.assertEqual(res.status_code, 201)

    def test_cannot_create_event_twice(self):
        self.register_user1()
        result = self.login_user1()
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # First event creation
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')

        # second event creation
        result = self.client.post('/api/events', headers=headers3, data=self.event1_data,
                                  content_type='application/json')
        self.assertIn(b'The event already exists', result.data)

    def test_cannot_create_event_with_invalid_details(self):
        self.register_user1()
        result = self.login_user1()
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # Name that is too short
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

        # Name that contains special characters and spaces
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

        # Location and category field containing numeric characters
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
        self.register_user1()
        result = self.login_user1()
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # create event first
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')

        # update the event
        res_1 = self.client.put('/api/events/1', headers=headers3, data=json.dumps(
            {
                'name': 'Bootcamp_Uganda',
                'category': 'Learning',
                'location': 'Uganda',
                'date_hosted': '8-8-2018',
                'description': 'This is the best learning experience'
            }
        ), content_type='application/json')
        self.assertIn(b'Bootcamp_Uganda', res_1.data)
        self.assertEqual(res_1.status_code, 200)

    def test_not_compulsory_to_update_all_fields(self):
        self.register_user1()
        result = self.login_user1()
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # create event first
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')

        # update the event but leave out the description field
        res_1 = self.client.put('/api/events/1', headers=headers3, data=json.dumps(
            {
                'name': 'Self_Learning_clinic',
                'category': '',
                'location': 'Nairobi',
                'date_hosted': '8-8-2018',
                'description': ''
            }
        ), content_type='application/json')
        # Confirm that the description still persists
        self.assertIn(b'This is the best learning experience', res_1.data)
        self.assertEqual(res_1.status_code, 200)

    def test_that_one_user_cannot_update_an_event_that_is_not_theirs(self):
        # Register and login the first user/user1
        self.register_user1()
        result = self.login_user1()
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # First user/user1 creates their event
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')

        # Register and login the second user/user2
        self.register_user2()
        result = self.login_user2()
        access_token2 = json.loads(result.data.decode())['token']
        headers4 = {'x-access-token': access_token2}

        # Second user/user2 creates their event
        res = self.client.post('/api/events', headers=headers4, data=self.event3_data, content_type='application/json')
        self.assertEqual(res.status_code, 201)

        # Second user/user2 tries to update an event belonging to the first user`s/user1
        res_1 = self.client.put('/api/events/1', headers=headers4, data=json.dumps(
            {
                'name': 'Bootcamp_Uganda',
                'category': 'Learning',
                'location': 'Uganda',
                'date_hosted': '8-8-2018',
                'description': 'This is the best learning experience'
            }
        ), content_type='application/json')
        # You get a notification that the event does not exist because it is not yours
        self.assertIn(b'The event does not exist', res_1.data)

    def test_that_you_cannot_update_an_event_that_does_not_exist(self):
        self.register_user1()
        result = self.login_user1()
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        res_1 = self.client.put('/api/events/14', headers=headers3, data=json.dumps(
            {
                'name': 'Bootcamp_Uganda',
                'category': 'Learning',
                'location': 'Uganda',
                'date_hosted': '8-8-2018',
                'description': 'This is the best learning experience'
            }
        ), content_type='application/json')
        self.assertIn(b'The event does not exist', res_1.data)

    def test_successful_deletion_of_an_event(self):
        self.register_user1()
        result = self.login_user1()
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # create event
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')

        # delete event
        res = self.client.delete('/api/events/1', headers=headers3)
        self.assertIn(b'Event deleted successfully', res.data)
        self.assertEqual(res.status_code, 200)

    def test_user_cannot_delete_an_event_that_is_not_his(self):
        # user1
        self.register_user1()
        result = self.login_user1()
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # event1 belonging to user1
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')

        # user2
        self.register_user2()
        result = self.login_user2()
        access_token2 = json.loads(result.data.decode())['token']
        headers4 = {'x-access-token': access_token2}

        res_1 = self.client.delete('/api/events/1', headers=headers4)
        self.assertIn(b'The event does not exist', res_1.data)

    def test_user_cannot_delete_an_event_that_does_not_exist(self):
        self.register_user1()
        result = self.login_user1()
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        res_1 = self.client.delete('/api/events/12', headers=headers3)
        self.assertIn(b'The event does not exist', res_1.data)

        # create event
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')

        # Delete the event once
        res = self.client.delete('/api/events/1', headers=headers3)
        self.assertIn(b'Event deleted successfully', res.data)
        self.assertEqual(res.status_code, 200)

        # Delete the event twice
        # Test that you cannot delete event twice and that event is deleted permanently
        res = self.client.delete('/api/events/1', headers=headers3)
        self.assertIn(b'The event does not exist', res.data)

    def test_get_specific_event(self):
        self.register_user1()
        result = self.login_user1()
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # First event
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')

        # second event
        self.client.post('/api/events', headers=headers3, data=self.event2_data, content_type='application/json')

        res_z = self.client.get('/api/event/1', headers=headers3)
        self.assertIn(b'Bootcamp', res_z.data)

    def test_cannot_get_an_event_you_have_not_created(self):
        # user1
        self.register_user1()
        result = self.login_user1()
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # user2
        self.register_user2()
        result = self.login_user2()
        access_token2 = json.loads(result.data.decode())['token']
        headers4 = {'x-access-token': access_token2}

        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')

        res_z = self.client.get('/api/event/3', headers=headers4)
        self.assertIn(b'No event created so far', res_z.data)

    def test_successful_retrieval_of_ones_overall_events(self):
        self.register_user1()
        result = self.login_user1()
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # First event
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')

        # second event
        self.client.post('/api/events', headers=headers3, data=self.event2_data, content_type='application/json')

        # Third event
        self.client.post('/api/events', headers=headers3, data=self.event3_data, content_type='application/json')

        result = self.client.get('/api/my_events', headers=headers3)
        events = json.loads(result.data.decode())['events']
        self.assertEqual(3, len(events))

    def test_cannot_retrieve_another_persons_overall_events(self):
        self.register_user1()
        result = self.login_user1()
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # First event belonging to user1
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')

        # second event belonging to user1
        self.client.post('/api/events', headers=headers3, data=self.event2_data, content_type='application/json')

        self.register_user2()
        result = self.login_user2()
        access_token2 = json.loads(result.data.decode())['token']
        headers4 = {'x-access-token': access_token2}

        # Third event
        self.client.post('/api/events', headers=headers4, data=self.event3_data, content_type='application/json')

        # fourth event
        self.client.post('/api/events', headers=headers4, data=self.event4_data, content_type='application/json')

        # Test how many events returned for first user
        result = self.client.get('/api/my_events', headers=headers3)
        events1 = json.loads(result.data.decode())['events']
        self.assertEqual(2, len(events1))

        # Test how many events returned for second user
        result = self.client.get('/api/my_events', headers=headers4)
        events2 = json.loads(result.data.decode())['events']
        self.assertEqual(2, len(events2))

    def test_successful_retrieval_of_all_events(self):
        self.register_user1()
        result = self.login_user1()
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # First event
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')

        # second event
        self.client.post('/api/events', headers=headers3, data=self.event2_data, content_type='application/json')

        # Third event
        self.client.post('/api/events', headers=headers3, data=self.event3_data, content_type='application/json')

        self.register_user2()
        result = self.login_user2()
        access_token2 = json.loads(result.data.decode())['token']
        headers4 = {'x-access-token': access_token2}

        # Forth event from user 2
        self.client.post('/api/events', headers=headers4, data=self.event4_data, content_type='application/json')

        result = self.client.get('/api/events')
        events = json.loads(result.data.decode())['events']
        self.assertEqual(4, len(events))

    def test_make_reservation_to_an_event(self):
        # user1
        self.register_user1()
        result = self.login_user1()
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # user2
        self.register_user2()
        result = self.login_user2()
        access_token2 = json.loads(result.data.decode())['token']
        headers4 = {'x-access-token': access_token2}

        # First event belonging to user1
        # User2 making a reservation to the event belonging to user1
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')
        result = self.client.post('/api/event/1/rsvp', headers=headers4)
        self.assertIn(b'You have made a reservation successfully', result.data)

    def test_that_you_cannot_make_a_reservation_twice(self):
        # user1
        self.register_user1()
        result = self.login_user1()
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # user2
        self.register_user2()
        result = self.login_user2()
        access_token2 = json.loads(result.data.decode())['token']
        headers4 = {'x-access-token': access_token2}

        # First event belonging to user1
        # User2 making a reservation to the event belonging to user1
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')
        result = self.client.post('/api/event/1/rsvp', headers=headers4)
        self.assertIn(b'You have made a reservation successfully', result.data)

        # Making the same reservation twice
        result = self.client.post('/api/event/1/rsvp', headers=headers4)
        self.assertIn(b'You cannot make a reservation twice', result.data)

    def test_that_an_event_returns_all_the_reservations(self):
        # user1
        self.register_user1()
        result = self.login_user1()
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # user2
        self.register_user2()
        result = self.login_user2()
        access_token2 = json.loads(result.data.decode())['token']
        headers4 = {'x-access-token': access_token2}

        # user3
        self.register_user3()
        result = self.login_user3()
        access_token3 = json.loads(result.data.decode())['token']
        headers6 = {'x-access-token': access_token3}

        # user1 creates event
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')

        # User2 makes a reservation
        self.client.post('/api/event/1/rsvp', headers=headers4)

        # User3 makes a reservation
        self.client.post('/api/event/1/rsvp', headers=headers6)

        # get the reservations
        result = self.client.get('/api/event/1/rsvp', headers=headers3)
        events = json.loads(result.data.decode())['Attendants']
        self.assertEqual(2, len(events))

    def test_that_you_see_reservations_unless_the_event_is_yours(self):
        # user1
        self.register_user1()
        result = self.login_user1()
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # user2
        self.register_user2()
        result = self.login_user2()
        access_token2 = json.loads(result.data.decode())['token']
        headers4 = {'x-access-token': access_token2}

        # user3
        self.register_user3()
        result = self.login_user3()
        access_token3 = json.loads(result.data.decode())['token']
        headers6 = {'x-access-token': access_token3}

        # user1 creates event
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')

        # User2 makes a reservation
        self.client.post('/api/event/1/rsvp', headers=headers4)

        # User3 makes a reservation
        self.client.post('/api/event/1/rsvp', headers=headers6)

        # User3 tries to see reservations made belonging to user1 event
        result = self.client.get('/api/event/1/rsvp', headers=headers4)
        self.assertEqual(result.status_code, 401)

    def test_successful_event_searching_by_location(self):
        # user1
        self.register_user1()
        result = self.login_user1()
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # user2
        self.register_user2()
        result = self.login_user2()
        access_token2 = json.loads(result.data.decode())['token']
        headers4 = {'x-access-token': access_token2}

        # Nairobi
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')

        # Uganda
        self.client.post('/api/events', headers=headers3, data=self.event2_data, content_type='application/json')

        # Mombasa
        self.client.post('/api/events', headers=headers3, data=self.event3_data, content_type='application/json')

        result = self.client.post('/api/search', headers=headers4, data=json.dumps({'location': 'Uganda'}),
                                  content_type='application/json')

        events = json.loads(result.data.decode())['Events found in this location']
        self.assertEqual(1, len(events))

        """Test that it cannot return an event if no event was hosted in the specified location"""
        result1 = self.client.post('/api/search', headers=headers4, data=json.dumps({'location': 'Kisumu'}),
                                   content_type='application/json')
        self.assertIn(b'There are no events organized in this location so far', result1.data)

    def test_successful_event_searching_by_category(self):
        # user1
        self.register_user1()
        result = self.login_user1()
        access_token1 = json.loads(result.data.decode())['token']
        headers3 = {'x-access-token': access_token1}

        # user2
        self.register_user2()
        result = self.login_user2()
        access_token2 = json.loads(result.data.decode())['token']
        headers4 = {'x-access-token': access_token2}

        # Learning
        self.client.post('/api/events', headers=headers3, data=self.event1_data, content_type='application/json')

        # Learning
        self.client.post('/api/events', headers=headers3, data=self.event2_data, content_type='application/json')

        # social
        self.client.post('/api/events', headers=headers3, data=self.event3_data, content_type='application/json')

        result = self.client.post('/api/search', headers=headers4, data=json.dumps({'category': 'learning'}),
                                  content_type='application/json')
        events = json.loads(result.data.decode())['Events belonging to this category']
        self.assertEqual(2, len(events))

        """Test that it cannot return an event if no event belongs to that category"""
        result1 = self.client.post('/api/search', headers=headers4, data=json.dumps({'category': 'Adventure'}),
                                   content_type='application/json')
        self.assertIn(b'There are no events related to this category', result1.data)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        del self.client


if __name__ == '__main__':
    unittest.main()
