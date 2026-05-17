import pytest

from tests.conftest import client, client_token


class TestLogin:
    """Integration tests for the authentication endpoints.
    These test the full request path — through middleware, the router,
    the auth service, the database — and check the HTTP response.
    """

    def test_login_success(self, client, app, db_session):
        """Valid credentials should return a JWT token with status 200."""
        from app.models.user import User

        with app.app_context():
            user = User(email='login@test.com', role='client')
            user.set_password('correctpassword')
            db_session.session.add(user)
            db_session.session.commit()

        response = client.post('/auth/login', json={
            'email': 'login@test.com',
            'password': 'correctpassword'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data, "Response should include an access_token"
        assert data['role'] == 'client'

    def test_login_wrong_password(self, client, app, db_session):
        """Wrong password should return 401 with no token in the response."""
        from app.models.user import User

        with app.app_context():
            user = User(email='wrongpw@test.com', role='client')
            user.set_password('correctpassword')
            db_session.session.add(user)
            db_session.session.commit()

        response = client.post('/auth/login', json={
            'email': 'wrongpw@test.com',
            'password': 'wrongpassword'
        })

        assert response.status_code == 401
        data = response.get_json()
        assert 'access_token' not in data

    def test_login_missing_fields(self, client):
        """A request with missing fields should return 400.
        No database setup needed — validation fails before the database is touched.
        """
        response = client.post('/auth/login', json={
            'email': 'someone@test.com'
            # password is missing
        })
        assert response.status_code == 400


class TestProtectedRoutes:
    """Integration tests verifying that route protection works correctly.
    These test the auth middleware layer — not the business logic inside routes.
    """

    def test_get_appointments_without_token(self, client):
        """A request with no token should be rejected with 401.
        401 means: I don't know who you are. Log in first.
        """
        response = client.get('/appointments')
        assert response.status_code == 401

    def test_get_appointments_with_client_token(self, client, client_token):
        """A client token on /appointments should return 200 with their own appointments.
        Clients are allowed on this route — they just get a filtered view, not full history.
        """
        response = client.get('/appointments', headers={
        'Authorization': f'Bearer {client_token}'
        })
        assert response.status_code == 200

    def test_get_appointments_with_stylist_token(self, client, stylist_token, db_session):
        """A stylist token on a stylist-only route should return 200."""
        response = client.get('/appointments', headers={
            'Authorization': f'Bearer {stylist_token}'
        })
        assert response.status_code == 200

    def test_get_services_is_public(self, client):
        """The services endpoint should be accessible with no token."""
        response = client.get('/services')
        assert response.status_code == 200