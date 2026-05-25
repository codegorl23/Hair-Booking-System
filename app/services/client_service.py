from app import db
from app.models.client import Client
import logging
logger = logging.getLogger(__name__)

def create_client(name, email):
    """
    Creates a new client.
    Returns (client, error_message, status_code).
    On success: (client_object, None, 201)
    On failure: (None, 'error message', error_code)
    """

    # Check that name and email are not empty strings
    if not name or not email:
        return None, 'name and email are required', 400

    # Check if email already exists in the database
    existing = Client.query.filter_by(email=email).first()
    if existing:
        return None, 'a client with that email already exists', 409

    # Create the new client
    client = Client(name=name, email=email)

    db.session.add(client)
    db.session.commit()
    
    logger.info(f"Client {client.id} registered successfully")
    return client, None, 201