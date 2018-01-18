from app import db


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
        return self.rsvps.filter_by(id=user.id).first() is not None

    def make_rsvp(self, user):
        if not self.check_reservation(user):
            self.rsvps.append(user)
            db.session.add(user)
            db.session.commit()

    # Return a printable representation of Event class object
    def __repr__(self):
        return "<Event(name='%s',category='%s',owner='%s')>" % (self.name, self.category, self.owner)
