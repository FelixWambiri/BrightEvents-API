from sqlalchemy import func

from app.init_db import db


class Event(db.Model):
    """
    This class is the blueprint for creating an event
    It avails the attributes required for an event
    """
    """
        Create an Events table
    """
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    category = db.Column(db.String(60), nullable=False)
    location = db.Column(db.String(60), nullable=False)
    owner = db.Column(db.String(60), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rsvps = db.relationship('Rsvp', backref='event')

    def __init__(self, name, category, location, owner, description, user_id):
        self.name = name
        self.category = category
        self.location = location
        self.owner = owner
        self.description = description
        self.user_id = user_id


class Rsvp(db.Model):
    """
        Create an Events table
    """
    __tablename__ = 'rsvps'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Method to add attendees into the attendants list
    def add_attendants(self, email):
        attendant = Rsvp.query.filter_by(email=email).first()
        if attendant:
            # User has already made a reservation
            return False
        else:
            db.session.add(attendant)
            db.commit()

    # Method to know the number of attendants
    def get_total_attendants(self):
        return db.session.query(func.count(Rsvp.id))
        