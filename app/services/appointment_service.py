from datetime import datetime, timedelta
from app import db
from app.models.appointment import Appointment
from app.models.service import Service
from app.models.client import Client
import logging

logger = logging.getLogger(__name__)


def create_appointment(client_id, service_id, start_time_str):
    """
    Creates a new appointment.
    Returns (appointment, error_message, status_code).
    On success: (appointment_object, None, 201)
    On failure: (None, 'error message', error_code)
    """
    logger.info(f"Appointment creation started: client_id={client_id} service_id={service_id}")
    # Parse the start_time string into a datetime object
    try:
        start_time = datetime.fromisoformat(start_time_str)
    except (ValueError, TypeError):
        return None, 'start_time must be a valid ISO datetime (e.g. 2026-04-15T10:00:00)', 400

    # Check start_time is in the future
    if start_time <= datetime.now():
        return None, 'start_time must be in the future', 400

    # Check the client exists
    client = db.session.get(Client,client_id)
    if not client:
        return None, f'No client found with id {client_id}', 404

    # Check the service exists
    service = db.session.get(Service,service_id)
    if not service:
        return None, f'No service found with id {service_id}', 404

    # Calculate end time from service duration
    end_time = start_time + timedelta(minutes=service.duration_mins)

    # Check for conflicting appointments
    conflict = Appointment.query.filter(
        Appointment.status == 'booked',
        Appointment.start_time < end_time,
        Appointment.end_time > start_time
    ).first()

    if conflict:
        logger.warning(f"Booking conflict: slot {start_time_str} is already taken")
        return None, 'This time slot is already booked', 409

    # Create the appointment
    appointment = Appointment(
        client_id=client_id,
        service_id=service_id,
        start_time=start_time,
        end_time=end_time,
        status='booked'
    )

    db.session.add(appointment)
    db.session.commit()
    logger.info(f"Appointment {appointment.id} created successfully for client_id={client_id}")
    return appointment, None, 201


def get_all_appointments():
    """
    Returns all appointments sorted by start_time ascending.
    Includes cancelled appointments — stylist needs full history.
    """
    appointments = Appointment.query.order_by(Appointment.start_time.asc()).all()
    return appointments


def get_appointment_by_id(appointment_id):
    """
    Returns a single appointment by ID.
    Returns (appointment, error_message, status_code).
    On success: (appointment_object, None, 200)
    On failure: (None, 'error message', 404)
    """
    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return None, f'No appointment found with id {appointment_id}', 404

    return appointment, None, 200


def update_appointment_status(appointment_id, status):
    """
    Updates the status of an appointment.
    Valid statuses: booked, cancelled, completed.
    Any status can be changed to any other valid status.
    Returns (appointment, error_message, status_code).
    On success: (appointment_object, None, 200)
    On failure: (None, 'error message', error_code)
    """

    valid_statuses = ['booked', 'cancelled', 'completed']

    # Check status is valid
    if status not in valid_statuses:
        logger.warning(f"Invalid status transition attempted: '{status}' is not a valid status")
        return None, f'status must be one of: {", ".join(valid_statuses)}', 400

    # Check appointment exists
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return None, f'No appointment found with id {appointment_id}', 404

    # Update the status
    appointment.status = status
    db.session.commit()

    return appointment, None, 200

def get_client_appointments(client_id):
    """
    Returns only upcoming booked appointments for a specific client.
    Clients should not see past or cancelled appointments.
    """
    appointments = Appointment.query.filter(
        Appointment.client_id == client_id,
        Appointment.status == 'booked',
        Appointment.start_time > datetime.now()
    ).order_by(Appointment.start_time.asc()).all()
    
    logger.info(f"Client {client_id} retrieved {len(appointments)} upcoming appointments")
    return appointments


def get_appointment_by_id_for_client(appointment_id, client_id):
    """
    Returns a single appointment for a client.
    Returns 404 if:
    - appointment doesn't exist
    - appointment belongs to another client
    - appointment is in the past
    - appointment is cancelled
    This prevents clients from knowing other appointments exist at all.
    """
    appointment = Appointment.query.filter(
        Appointment.id == appointment_id,
        Appointment.client_id == int(client_id),
        Appointment.status == 'booked',
        Appointment.start_time > datetime.now()
    ).first()

    if not appointment:
        return None, f'No appointment found with id {appointment_id}', 404

    return appointment, None, 200