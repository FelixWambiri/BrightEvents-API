--bind 0.0.0.0:$PORT
python manage.py db upgrade
web: waitress-serve run:app