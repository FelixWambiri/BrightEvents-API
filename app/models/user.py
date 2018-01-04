from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.models.event import Event
from app.views import db


class User(UserMixin, db.Model):
    """
    Blue print for creating the user of the app
    With all their attributes and methods
    """

    def __init__(self, username, email, password):
        self.username = username
        self.id = email
        self.password = password

    """
    Create a User table
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(70), index=True, nullable=False)
    email = db.Column(db.String(70), index=True, unique=True, nullable=False)
    password = db.Column(db.String(128))
    events = db.relationship('Event', backref='user')

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
        event_f = Event.query.filter_by(event.name).first()
        if event_f:
            # Event already exists
            return False
        db.session.add(event)
        db.commit()
        return True

    # Deletes an event but first checks if it exists
    def delete_event(self, event):
        db.session.delete(event)
        db.session.commit()

    # This method returns a specific event
    def get_specific_event(self, event):
        event_f = Event.query.filter_by(event.name).first()
        if event_f:
            return event_f
        else:
            print('There is no such event')
            return False

    # Method for User to change password
    def user_reset_password(self, new_pass):
        pass_hash = generate_password_hash(new_pass)
        self.pw_hash = pass_hash

    # Return a printable representation of User class object
    def __repr__(self):
        return '<User %r>' % self.email
