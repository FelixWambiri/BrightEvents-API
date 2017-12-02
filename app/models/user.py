from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin):
    """
    Blue print for creating the user of the app
    With all their attributes and methods
    """

    def __init__(self, username, email, password):
        self.username = username
        self.id = email
        self.pw_hash = generate_password_hash(password)
        self.events_dict = {}

    # Method to verify the hashed password
    def compare_hashed_password(self, password):
        return check_password_hash(self.pw_hash, password)

    # Create an event whereby name is key
    # But first check if the event already exists
    def create_event(self, event):
        if event.name in self.events_dict:
            raise KeyError("You already have an event by the name" + event.name + "Please use another name")
        else:
            return self.events_dict.update({event.name: event})

    # Update an event but first check if the user wants to update that field
    # If event field is empty previous data is retained
    def update_event(self, name, new_name, category, location, owner, description):
        event = self.events_dict[name]
        event = self.events_dict[name]
        if new_name != '':
            event.name = new_name
            self.events_dict[new_name] = event
            del self.events_dict[name]
        if category != '':
            event.category = category

        if location != '':
            event.location = location

        if owner != '':
            event.owner = owner

        if description != '':
            event.description = description

        return event

    # Deletes an event but first checks if it exists
    def delete_event(self, name):
        if name not in self.events_dict:
            raise KeyError("There does not exist an event by that name")
        else:
            return self.events_dict.pop(name)

    # This method returns a specific event
    def get_specific_event(self, event_name):
        if event_name in self.events_dict:
            return self.events_dict[event_name]
        else:
            raise KeyError("The event does not exist")

    # Method to return the total number of events
    def get_number_of_events(self):
        return len(self.events_dict)
