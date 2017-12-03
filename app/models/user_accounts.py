class UserAccounts:
    """
    Blue print for creating and managing users
    Contains user accounts attributes method
    It will be responsible for displaying all events
    """

    def __init__(self):
        self.users = {}
        self.events = {}

    # Add a new user into the database
    def create_user(self, user):
        if user.id in self.users:
            raise KeyError("There exists a user with that name. Please use another name")
        else:
            return self.users.update({user.id: user})

    # Return a specific user
    def get_specific_user(self, email):
        if email in self.users:
            return self.users[email]

    # Delete a user
    def delete_user(self, email):
        try:
            self.users.pop(email)
        except KeyError:
            print("The User does not exist")
            raise

    # Method to add users individual events into the general events dictionary
    # Fix a bug in this method have to delete event because after updating event the original remained
    def add_all_individual_events(self, previous_event, user):
        if user.id in self.users:
            if previous_event in self.events:
                del self.events[previous_event]
            return self.events.update(user.events_dict)

    # Returns the total number of users events in the events dictionary
    def get_number_of_all_users_events(self):
        return len(self.events)

    #  Method to delete an individuals event from the public events list/page
    def delete_an_individuals_events(self, event_name):
        return self.events.pop(event_name)
