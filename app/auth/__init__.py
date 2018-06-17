from flask import Blueprint
from flask_cors import CORS

auth = Blueprint('auth', __name__)
from app.auth import views
CORS(auth)
