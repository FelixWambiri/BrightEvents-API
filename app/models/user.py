from datetime import date

from sqlalchemy import cast, Date
from werkzeug.security import generate_password_hash, check_password_hash

from app.init_db import db
from app.models.event import Event


class User(db.Model):
    """
    Blue print for creating the user of the app
    With all their attributes and methods
    """
    """
    Create a Rsvp table to show which events a user has made a reservation to
    This table user a many to many relationship
    """
    rsvps = db.Table('rsvps',
                     db.Column('user_id', db.ForeignKey('users.id'), primary_key=True),
                     db.Column('event_id', db.ForeignKey('events.id'), primary_key=True)
                     )
    """
       Create a User table
       """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, nullable=False)
    email = db.Column(db.String(64), index=True, unique=True, nullable=False)
    pw_hash = db.Column(db.String(100))
    events = db.relationship('Event', back_populates='user')
    ind_rsvps = db.relationship('Event', secondary=rsvps, backref=db.backref('rsvps', lazy='dynamic'))

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

    def create_event(self, name, category, location, date_hosted, description):
        """
        Method creates an event by first checking its existence and raising an integrity error if in existence
        :param date_hosted:
        :param name:
        :param category:
        :param location:
        :param description:
        :return:
        """

        event = Event.query.filter_by(name=name).filter_by(category=category).filter_by(owner=self.id).filter_by(
            date_hosted=date_hosted).first()
        if not event:
            event = Event(name=name, category=category, location=location, owner=self.id, date_hosted=date_hosted,
                          description=description, )
            db.session.add(event)
            db.session.commit()
            return event

    def update_event(self, event_id=None, name=None, category=None, location=None, date_hosted=None, description=None):
        """
        Method updates an event and if the field is empty it populates that field with previously stored info
        :param event_id:
        :param date_hosted:
        :param name:
        :param category:
        :param location:
        :param description:
        :return:
        """
        event = Event.query.filter_by(id=event_id).filter_by(owner=self.id).first()
        if event:
            if name.strip():
                event.name = name

            if category.strip():
                event.category = category

            if location.strip():
                event.location = location

            if date_hosted.strip():
                event.date_hosted = date_hosted

            if description.strip():
                event.description = description

            u_event = Event.query.filter_by(name=event.name).filter_by(category=event.category).filter_by(
                owner=self.id).filter_by(
                date_hosted=event.date_hosted).first()

            if u_event.id != event.id:
                return "You cannot update an event to duplicate an existing event"
            else:
                db.session.commit()
                return event
        print('The event does not exist')

    def delete_event(self, event_id):
        """
        Methods deletes an event give the name of the event
        :param event_id:
        :return:
        """
        event = Event.query.filter_by(id=event_id).filter_by(owner=self.id).first()
        if event:
            db.session.delete(event)
            db.session.commit()
        else:
            raise AttributeError

    def get_specific_event(self, event_id):
        """
        This method returns a specific event when given the events name
        :param event_id:
        :return:
        """
        try:
            event = Event.query.filter_by(id=event_id).filter_by(owner=self.id).first()
            return event
        except AttributeError:
            print('The event you are trying to retrieve does not exist')
            return False

    def get_number_of_events(self):
        """
        This method queries and returns the total number of events a person has created
        :return:
        """
        return Event.query.filter_by(owner=self.id).count()

    @staticmethod
    def search_event_by_name(name, page=1):
        return Event.query.filter(Event.name.ilike("%" + name + "%")).order_by(Event.date_hosted.desc()).paginate\
            (page, per_page=4, error_out=True).items

    @staticmethod
    def search_event_by_category(category, page=1):
        """This method searches an event by category and is case insensitive"""

        return Event.query.filter(Event.category.ilike("%" + category + "%")).filter(
            cast(Event.date_hosted, Date) >= date.today()).order_by(Event.date_hosted.desc()).paginate \
            (page, per_page=3, error_out=True).items

    @staticmethod
    def search_event_by_location(location, page=1):
        """This method searches an event by location and is case insensitive"""
        return Event.query.filter(Event.location.ilike("%" + location + "%")).filter(
            cast(Event.date_hosted, Date) >= date.today()).order_by(Event.date_hosted.desc()).paginate \
            (page, per_page=3, error_out=True).items

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
