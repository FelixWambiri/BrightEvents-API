from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app.init_db import db
from app.models.event import Event
from app.models.user import User


class UserAccounts:
    """
    Blue print for creating and managing users
    Contains user accounts attributes method
    It will be responsible for displaying all events
    """

    # Add a new user into the database
    def create_user(self, user):
        user_f = User.query.filter_by(email=user.email).first()
        if user_f:
            raise IntegrityError("There exists a user with that email. Please use another email")
        else:
            db.session.add(user_f)
            db.commit()
            return True

    # Return a specific user
    def get_specific_user(self, email):
        return User.query.filter_by(email=email).first()

    # Delete a user
    def delete_user(self, email):
        user = User.query.filter_by(email=email).first()
        if user:
            db.session.delete(user)
            db.session.commit()
        else:
            raise IntegrityError("The User does not exist")

    # Returns the total number of users events in the events dictionary
    def get_number_of_all_users_events(self):
        return db.session.query(func.count(User.id))

    #  Method to delete an individuals event from the public events list/page
    def delete_an_individuals_events(self, name):
        event = Event.query.filter_by(name=name).first()
        db.session.delete(event)
        db.session.commit()
