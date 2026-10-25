import unittest
from unittest.mock import patch

from sqlalchemy.exc import SQLAlchemyError
from app import create_app


class TestConfig:
    SECRET_KEY = 'test-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class HealthAndAuthRouteTests(unittest.TestCase):
    def setUp(self):
        app = create_app(TestConfig)
        app.config.update(TESTING=True, WTF_CSRF_ENABLED=False, SQLALCHEMY_DATABASE_URI='sqlite:///:memory:')
        self.app = app
        self.client = app.test_client()

    def test_health_endpoint(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.get_json())
        self.assertEqual(response.get_json()['database'], 'connected')

    def test_health_endpoint_reports_database_failure(self):
        with patch('app.routes.main.db.session.execute', side_effect=SQLAlchemyError('database unavailable')):
            response = self.client.get('/health')

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.get_json()['database'], 'unavailable')

    def test_auth_pages_are_accessible(self):
        login_response = self.client.get('/auth/login')
        register_response = self.client.get('/auth/register')
        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(register_response.status_code, 200)

    def test_map_page_is_accessible(self):
        response = self.client.get('/map')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Leaflet', response.get_data(as_text=True))


if __name__ == '__main__':
    unittest.main()
