import pytest
from datetime import datetime, timedelta
from app.services.appointment_service import create_appointment
from app.models.service import Service
from tests.conftest import client_token

class TestCreateAppointment:
    """Unit tests for the create_appointment service function.

    Each method tests one specific behaviour. The method name describes
    exactly what behaviour is being tested and what the expected outcome is.
    """

    def test_create_appointment_success(self, app, db_session, sample_service):
        """A valid appointment should be created and returned with status 201."""
        from app.models.client import Client

        with app.app_context():
            service= db_session.session.get(Service,sample_service)
            # Arrange: create a client and a future timestamp
            client = Client(name='Test Client', email='test@example.com')
            db_session.session.add(client)
            db_session.session.commit()

            # timedelta(days=1) = one day from now — always in the future
            future_time = (datetime.now() + timedelta(days=1)).isoformat()

            # Act: call create_appointment directly — no HTTP involved
            appointment, error, status_code = create_appointment(
                client_id=client.id,
                service_id=service.id, 
                start_time_str=future_time
            )

            # Assert: check every meaningful property of the result
            assert error is None, f"Expected no error but got: {error}"
            assert status_code == 201, f"Expected 201 but got: {status_code}"
            assert appointment is not None
            assert appointment.client_id == client.id
            assert appointment.service_id == service.id
            assert appointment.status == 'booked'

    def test_create_appointment_past_time_rejected(self, app, db_session, sample_service):
        """An appointment in the past should be rejected with status 400."""
        from app.models.client import Client

        with app.app_context():
            service = db_session.session.get(Service, sample_service)

            client = Client(name='Past Client', email='past@example.com')
            db_session.session.add(client)
            db_session.session.commit()

            # subtracting timedelta = one day in the past
            past_time = (datetime.now() - timedelta(days=1)).isoformat()

            appointment, error, status_code = create_appointment(
                client_id=client.id,
                service_id=service.id,
                start_time_str=past_time
            )

            assert appointment is None
            assert status_code == 400
            assert error is not None

    def test_create_appointment_conflict_rejected(self, app, db_session, sample_service):
        """Booking the same slot twice should fail on the second attempt with 409."""
        from app.models.client import Client

        with app.app_context():
            service = db_session.session.get(Service, sample_service)

            client = Client(name='Conflict Client', email='conflict@example.com')
            db_session.session.add(client)
            db_session.session.commit()

            future_time = (datetime.now() + timedelta(days=2)).isoformat()

            # First booking — should succeed
            first, _, _ = create_appointment(
                client_id=client.id,
                service_id=service.id,
                start_time_str=future_time
            )
            assert first is not None, "First booking should have succeeded"

            # Second booking at the same time — should fail
            appointment, error, status_code = create_appointment(
                client_id=client.id,
                service_id=service.id,
                start_time_str=future_time
            )

            assert appointment is None
            assert status_code == 409

    def test_create_appointment_nonexistent_client(self, app, db_session, sample_service):
        """Using a client_id that doesn't exist should return 404."""
        with app.app_context():
            service = db_session.session.get(Service, sample_service)

            future_time = (datetime.now() + timedelta(days=3)).isoformat()

            appointment, error, status_code = create_appointment(
                client_id=99999,  # this ID does not exist in the test database
                service_id=service.id,
                start_time_str=future_time
            )

            assert appointment is None
            assert status_code == 404

    def test_create_appointment_invalid_datetime(self, app, db_session, sample_service):
        """A start_time that cannot be parsed should return 400."""
        from app.models.client import Client

        with app.app_context():
            service = db_session.session.get(Service, sample_service)

            client = Client(name='Invalid Client', email='invalid@example.com')
            db_session.session.add(client)
            db_session.session.commit()

            appointment, error, status_code = create_appointment(
                client_id=client.id,
                service_id=service.id,
                start_time_str='this is not a datetime'  # unparseable
            )

            assert appointment is None
            assert status_code == 400
    