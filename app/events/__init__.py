from flask import Blueprint
from flask_cors import CORS

event = Blueprint('events', __name__)
from app.events import views
CORS(event)

