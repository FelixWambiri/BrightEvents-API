from flask_login import UserMixin
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

from app.init_db import db
from app.models.event import Event


class User(UserMixin, db.Model):
    """
    Blue print for creating the user of the app
    With all their attributes and methods
    """
    """
       Create a User table
       """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(70), index=True, nullable=False)
    email = db.Column(db.String(70), index=True, unique=True, nullable=False)
    password = db.Column(db.String(128))
    events = db.relationship('Event', backref='user')
    rsvps = db.relationship('RSVP', backref='rsvp')

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    @property
    def password(self):
        """
        Prevent the password from being accessed
        """

        raise AttributeError('password is not a readable attribute.')

    # Method to hash the password
    @password.setter
    def password(self, password):
        """
        Set password to a hashed password
        """
        self.pw_hash = generate_password_hash(password)

    # Method to verify the hashed password
    def compare_hashed_password(self, password):
        """
        To verify if the hashed password matches the actual password
        """
        return check_password_hash(self.pw_hash, password)

    # Create an event whereby name is key
    # But first check if the event already exists
    def create_event(self, event):
        event_f = Event.query.filter_by(name=event.name).first()
        if event_f:
            # Event already exists
            return False
        else:
            db.session.add(event_f)
            db.session.commit()
            return True

    # Update an event but first check if the user wants to update that field
    # If event field is empty previous data is retained
    # Avoid spaces by using strip function
    def update_event(self, name, new_name, category, location, owner, description):
        event = Event.query.filter_by(name=name).first()
        if new_name.strip():
            event.name = new_name

        if category.strip():
            event.category = category

        if location.strip():
            event.location = location

        if owner.strip():
            event.owner = owner

        if description.strip():
            event.description = description
        db.session.add(event)
        db.commit()

    # Deletes an event but first checks if it exists
    def delete_event(self, name):
        event = Event.query.filter_by(name=name).first()
        if event:
            db.session.delete(event)
            db.session.commit()
        else:
            raise IntegrityError("There does not exist an event by that name")

    # This method returns a specific event given the name of the event
    def get_specific_event(self, name):
        event = Event.query.filter_by(name=name).first()
        if event:
            return event
        else:
            print('There is no such event')
            return False

    # Method to return the total number of events
    def get_number_of_events(self):
        return db.session.query(func.count(User.id))

    # Method for User to change password
    def user_reset_password(self, new_pass):
        pass_hash = generate_password_hash(new_pass)
        self.pw_hash = pass_hash

    # Return a printable representation of User class object
    def __repr__(self):
        return '<User %r>' % self.id
