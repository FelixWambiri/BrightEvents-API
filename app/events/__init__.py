from flask import Blueprint

event = Blueprint('events', __name__)
from app.events import views

