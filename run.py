"""Entry point to start our app"""
import os

from app import create_app

development = os.getenv('APP_SETTINGS')
app = create_app(config_name='development')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
