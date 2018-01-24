# tests/test_config.py


import unittest
from unittest import TestCase

from app import create_app


class TestDevelopmentConfig(TestCase):
    def test_app_is_development(self):
        app = create_app(config_name='development')
        self.assertFalse(app.config['SECRET_KEY'] is 'This_is_my_year')
        # self.assertFalse(current_app is None)
        self.assertTrue(
            app.config['SQLALCHEMY_DATABASE_URI'] == 'postgresql://postgres:AndelaFellow2017@localhost/BrightEventDb'
        )


class TestTestingConfig(TestCase):
    def test_app_is_testing(self):
        app = create_app(config_name='testing')
        self.assertFalse(app.config['SECRET_KEY'] is 'This_is_my_year')
        self.assertTrue(
            app.config[
                'SQLALCHEMY_DATABASE_URI'] == 'postgresql://postgres:AndelaFellow2017@localhost/BrightEventTestDb'
        )


class TestProductionConfig(TestCase):
    def test_app_is_production(self):
        app = create_app(config_name='production')
        self.assertTrue(app.config['DEBUG'] is False)


if __name__ == '__main__':
    unittest.main()
