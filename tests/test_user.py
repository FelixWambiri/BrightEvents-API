import unittest

from app.models.user import User
from app.models.event import Event


class TestUser(unittest.TestCase):
    """
    This class will test:
        If the methods of the User class are working correctly
        If not, whether that is captured
    """

    def setUp(self):
        """
        Instantiating reusable variables
        """
        self.user = User("Fellow1", "fellow1@andela.com", "bootcampertofellow")
        self.event1 = Event("Bootcamp", "Learning", "Uganda", "Andela", "Learning event for aspiring Andelans")
        self.event2 = Event("Blaze", "Entrepreneurial", "Kenya", "Safariom",
                            "This is is a great opportunity for budding young entrepreneurs")
        self.event3 = Event("Blankets and wines", "Social", "Kenya", "B&W", "Chance for everyone to meet and socialise")

    # Test for successful creation of a new user
    def test_user_is_created(self):
        self.assertEqual(isinstance(self.user, User), True)

    # Test that at initialisation user has no events
    def test_that_initially_user_has_no_event(self):
        self.assertEqual(0, len(self.user.events_dict))

    # Test if create event method works
    def test_create_event_works(self):
        self.user.create_event(self.event1)
        self.assertEqual(1, len(self.user.events_dict))

    # Test if user can create and add multiple events
    def test_user_can_create_multiple_events(self):
        # First event
        self.user.create_event(self.event1)
        self.assertEqual(1, len(self.user.events_dict))

        # Second and third event
        self.user.create_event(self.event2)
        self.user.create_event(self.event3)
        self.assertEqual(3, len(self.user.events_dict))

    # Test method raises exception on addition of an event in existence
    def test_user_cannot_add_an_already_existing_event(self):
        self.event4 = Event("Blaze", "Entrepreneurial", "Kenya", "Safariom",
                            "This is is a great opportunity for budding young entrepreneurs")
        self.user.create_event(self.event2)
        self.assertRaises(KeyError, self.user.create_event, self.event4)

    # Test that a user can delete an event
    def test_user_can_delete_events(self):
        self.user.create_event(self.event1)
        self.user.create_event(self.event2)
        self.user.create_event(self.event3)
        self.assertEqual(3, len(self.user.events_dict))

        # Delete a single event, event1
        self.user.delete_event("Bootcamp")
        self.assertEqual(2, len(self.user.events_dict))

        # Delete the remaining events
        self.user.delete_event("Blaze")
        self.user.delete_event("Blankets and wines")
        self.assertEqual(0, len(self.user.events_dict))

    # Test method raises exception on attempt to delete an event that does not exist
    def test_method_raises_exception_on_deletion_of_non_existent_event(self):
        # creating an event but not adding it to the database to pass it as a parameter in our method
        self.event4 = Event("Blaze", "Entrepreneurial", "Kenya", "Safariom",
                            "This is is a great opportunity for budding young entrepreneurs")
        self.assertRaises(KeyError, self.user.delete_event, "Blaze")

        # Test that once an event is deleted it is completely wiped of from the database
        # Create the event
        self.user.create_event(self.event1)

        # Delete it the first instance
        self.user.delete_event("Bootcamp")
        self.assertEqual(0, len(self.user.events_dict))

        # Delete it second time and see if it captures the exception
        self.assertRaises(KeyError, self.user.delete_event, "Bootcamp")

    # Test that the method get_specific_event returns that specified event
    def test_get_specific_event_method_returns_correct_output(self):
        self.user.create_event(self.event1)
        self.assertIs(self.event1, self.user.get_specific_event("Bootcamp"))

    # Test that an event can be updated
    def test_successful_update_of_event(self):
        self.user.create_event(self.event1)
        self.assertEqual(self.event1,
                         self.user.update_event("Bootcamp", "Bootcamp 20", "social", "tanzania", "safaricom", "eating contest"))

    # Test that the correct number of events is returned
    def test_that_get_number_of_events_method_returns_correct_output(self):
        # Test when there is no event added
        self.assertEqual(0, self.user.get_number_of_events())

        # Test after creating three events
        self.user.create_event(self.event1)
        self.user.create_event(self.event2)
        self.user.create_event(self.event3)
        self.assertEqual(3, self.user.get_number_of_events())


if __name__ == '__main__':
    unittest.main()


