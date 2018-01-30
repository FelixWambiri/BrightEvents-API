from app.init_db import db


class Event(db.Model):
    """
    This class is the blueprint for creating an event
    It avails the attributes required for an event
    """
    """
        Create an Events table
    """
    __searchable__ = ['category', 'location']
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    category = db.Column(db.String(64), nullable=False)
    location = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(180), nullable=True)
    owner = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='events')

    def __init__(self, name, category, location, owner, description):
        self.name = name
        self.category = category
        self.location = location
        self.owner = owner
        self.description = description

    def check_reservation(self, user):
        return self.rsvps.filter_by(id=user.id).first()

    def make_rsvp(self, user):
        if self.check_reservation(user) is None:
            self.rsvps.append(user)
            db.session.add(user)
            db.session.commit()
        else:
            raise AttributeError(
                "You cannot make a reservation twice and you cannot make a reservation to your own event")


# Return a printable representation of Event class object
def __repr__(self):
    return "<Event(name='%s',category='%s',owner='%s')>" % (self.name, self.category, self.owner)
