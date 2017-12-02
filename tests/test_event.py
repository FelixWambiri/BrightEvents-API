import unittest

from app.models.event import Event
from app.models.user import User


class TestEvent(unittest.TestCase):
    """
    This class will test:
        If the of the Event class are working correctly
        If not, whether that is captured
    """

    def setUp(self):
        """
        Instantiating reusable variables
        """
        self.event = Event("Bootcamp", "Learning", "Uganda", "Andela", "Learning event for aspiring Andelans")
        self.attendant = User("Fellow1", "fellow1@andela.com", "bootcampertofellow")
        self.attendant1 = User("Johny", "johny@bravo.com", "johnybravobravo")
        self.attendant2 = User("Ricky", "ricky@morty.com", "rickandmorty")

    # Test for successful creation of a new attendant
    def test_attendant_is_created(self):
        self.assertEqual(isinstance(self.attendant, User), True)

    # Test for successful creation of an event
    def test_event_is_created(self):
        self.assertEqual(isinstance(self.event, Event), True)

    # Test that at initialisation event has no attendants
    def test_that_initially_event_has_no_attendees(self):
        self.assertEqual(0, len(self.event.event_attendees))

    # Test that an event attendant is added into the attendants database
    def test_attendant_is_added_to_the_attendants_list(self):
        self.event.add_attendants(self.attendant)
        self.assertEqual(1, len(self.event.event_attendees))

    # Test that multiple attendants can attend one event
    def test_that_multiple_attendants_can_attend_one_event(self):
        # Add 1st attendant
        self.event.add_attendants(self.attendant)

        # Add 2nd attendant
        self.event.add_attendants(self.attendant1)

        # Add 3rd attendant
        self.event.add_attendants(self.attendant2)

        # Test that three of them are added to attend the event
        self.assertEqual(3, len(self.event.event_attendees))

    # Test that the correct number of event attendants is returned
    def test_that_get_total_attendants_method_returns_correct_output(self):
        # Test when there is no event added
        self.assertEqual(0, self.event.get_total_attendants())

        # Test after adding one attendant
        self.event.add_attendants(self.attendant)
        self.assertEqual(1, self.event.get_total_attendants())

        # Test after adding two attendants
        self.event.add_attendants(self.attendant1)
        self.event.add_attendants(self.attendant2)
        self.assertEqual(3, self.event.get_total_attendants())


if __name__ == '__main__':
    unittest.main()

