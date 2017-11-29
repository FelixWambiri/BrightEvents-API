class Event:
    """
    This class is the blueprint for creating an event
    It avails the attributes required for an event
    """

    def __init__(self, name, category, location, owner, description):
        self.name = name
        self.category = category
        self.location = location
        self.owner = owner
        self.description = description
        self.event_attendees = []

    # Method to add attendees into the attendants list
    def add_attendants(self, attendant):
        return self.event_attendees.append(attendant)

    # Method to know the number of attendants
    def get_total_attendants(self):
        return len(self.event_attendees)


