from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from app.init_db import db
from app.models.event import Event
from app.models.user import User


class UserAccounts:
    """ Creates and manages individual user accounts """

    @staticmethod
    def create_user(username, email, password):
        """
        Method adds a new user to the database after confirming that the user does not already exist.The email should
         be unique
        :param username:
        :param email:
        :param password:
        :return:
        """
        try:
            user = User(username=username, email=email, password=password)
            db.session.add(user)
            db.session.commit()
            return user
        except IntegrityError:
            db.session.rollback()
            print('There exists user with that email address.Please choose another email')

    @staticmethod
    def get_specific_user(email):
        """
        This method should return one specific user given the email address of that user
        :param email:
        :return:
        """
        try:
            user = User.query.filter_by(email=email).one()
            return user
        except NoResultFound:
            return False

    @staticmethod
    def delete_user(email):
        """
        This method deletes a specific user  given their email address
        :param email:
        :return:
        """
        try:
            user = User.query.filter_by(email=email).one()
            db.session.delete(user)
            db.session.commit()
        except NoResultFound:
            print("The user you are trying to delete does not exist")

    @staticmethod
    def get_number_of_all_users_events():
        """
        This method queries the database and returns the total number of all the events present in the database
        :return:
        """
        return Event.query.count()
