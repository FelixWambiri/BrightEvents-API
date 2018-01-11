from flask_login import UserMixin
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
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
    username = db.Column(db.String(64), index=True, nullable=False)
    email = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password = db.Column(db.String(100))
    events = db.relationship('Event', back_populates='user')
    rsvps = db.relationship('Rsvp', back_populates='user')

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

    @password.setter
    def password(self, password):
        """
        Set password to a hashed password
        """
        self.pw_hash = generate_password_hash(password)

    def compare_hashed_password(self, password):
        """
        To verify if the hashed password matches the actual password
        """
        return check_password_hash(self.pw_hash, password)

    def create_event(self, name, category, location, owner, description):
        """
        Method creates an event by first checking its existence and raising an integrity error if in existence
        :param name:
        :param category:
        :param location:
        :param owner:
        :param description:
        :return:
        """
        event_f = Event.query.filter_by(name=name).filter_by(owner=owner).first()
        if event_f:
            try:
                event = Event(name=name, category=category, location=location, owner=owner, description=description)
                db.session.add(event)
                db.session.commit()
                return True
            except IntegrityError:
                db.session.rollback()
                print('There exists an event with that name already.Please choose another name')

    def update_event(self, name, new_name, category, location, description, owner):
        """
        Method updates an event and if the field is empty it populates that field with previously stored info
        :param owner:
        :param name:
        :param new_name:
        :param category:
        :param location:
        :param description:
        :return:
        """
        try:
            event = Event.query.filter_by(name=name).filter_by(owner=owner).first()
            if new_name.strip():
                event.name = new_name

            if category.strip():
                event.category = category

            if location.strip():
                event.location = location

            if description.strip():
                event.description = description
            db.session.commit()

        except AttributeError:
            print('The event you want to update does not exist')

    def delete_event(self, name, owner):
        """
        Methods deletes an event give the name of the event
        :param owner:
        :param name:
        :return:
        """
        try:
            event = Event.query.filter_by(name=name).filter_by(owner=owner).one()
            db.session.delete(event)
            db.session.commit()
        except NoResultFound:
            print("The event you are trying to delete does not exist")

    def get_specific_event(self, name, owner):
        """
        This method returns a specific event when given the events name
        :param owner:
        :param name:
        :return:
        """
        try:
            event = Event.query.filter_by(name=name).filter_by(owner=owner).first()
            return "<Event(name='%s',category='%s',owner='%s')>" % (event.name, event.category, event.owner)
        except AttributeError:
            print('The event you are trying to retrieve does not exist')
            return False

    def get_number_of_events(self, owner):
        """
        This method queries and returns the total number of events a person has created
        :return:
        """
        return Event.query.filter_by(owner=owner).count()

    def user_reset_password(self, new_pass):
        """
        Method to reset the password to a new value
        :param new_pass:
        :return:
        """
        pass_hash = generate_password_hash(new_pass)
        self.pw_hash = pass_hash

    def __repr__(self):
        return '<User %r>' % self.username
