from flask_login import UserMixin


class User(UserMixin):
    """
    Blue print for creating the user of the app
    With all their attributes and methods
    """

    def __init__(self, username, email, password, confirm_password):
        self.id = username
        self.email = email
        self.password = password
        self.confirm_password = confirm_password
        self.events_dict = {}

    # Create an event whereby name is key
    # But first check if the event already exists
    def create_event(self, event):
        if event.name in self.events_dict:
            raise KeyError("You already have an event by the name" + event.name + "Please use another name")
        else:
            return self.events_dict.update({event.name: event})

    # Update an event but first check if the user wants to update that field
    # If event field is empty previous data is retained
    def update_event(self, name, category, location, owner, description):
        event = self.events_dict[name]
        print('category is ...', type(category))
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
    def get_specific_event(self, event):
        if event.name in self.events_dict:
            return self.events_dict[event.name]
        else:
            raise KeyError("The event does not exist")

    # Method to return the total number of events
    def get_number_of_events(self):
        return len(self.events_dict)
