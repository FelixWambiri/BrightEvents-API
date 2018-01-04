from app.views import db


class Event(db.Model):
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

