class TestCreateClient:
    """Integration tests for the POST /clients endpoint."""

    def test_create_client_duplicate_email_rejected(self, client, app, db_session):
        """Creating a client with an email that already exists should return 409."""
        from app.models.client import Client

        with app.app_context():
            # Arrange: create a client that already exists in the database
            existing_client = Client(name='Existing Client', email='client@test.com')
            db_session.session.add(existing_client)
            db_session.session.commit()

        # Act: try to POST a new client with the same email
        response = client.post('/clients', json={
            'name': 'Client 2',
            'email': 'client@test.com'  # same email as above — triggers 409
        })

        # Assert: duplicate should be rejected
        assert response.status_code == 409