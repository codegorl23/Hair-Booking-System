import pytest
from app import create_app, db as _db
from app.models.user import User
from app.models.service import Service
from app.models.client import Client


@pytest.fixture(scope='session')
def app():
    """Create a Flask app configured for testing.
    Created once for the entire test session.
    """
    test_app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-secret-key-not-for-production',
    })
    return test_app


@pytest.fixture(scope='session')
def db(app):
    """Create all database tables once for the test session.
    Dropped when all tests finish.
    """
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()


@pytest.fixture(scope='function')
def db_session(db):
    """Wrap each test in a transaction that rolls back after.
    This ensures every test starts with a clean database.
    """
    connection = db.engine.connect()
    transaction = connection.begin()
    db.session.bind = connection

    yield db

    db.session.remove()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope='function')
def client(app):
    """Flask test client — sends HTTP requests to your app without a network.
    Created fresh for every test.
    """
    return app.test_client()


@pytest.fixture(scope='function')
def stylist_token(app, db_session):
    """Create a stylist user in the test database and return a valid JWT for them."""
    from flask_jwt_extended import create_access_token
    with app.app_context():
        user = User(email='stylist@test.com', role='stylist')
        user.set_password('password123')
        db_session.session.add(user)
        db_session.session.commit()
        token = create_access_token(
            identity=str(user.id),
            additional_claims={'role': 'stylist'}
        )
    return token


@pytest.fixture(scope='function')
def client_token(app, db_session):
    """Create a client user in the test database and return a valid JWT for them."""
    from flask_jwt_extended import create_access_token
    with app.app_context():
        user = User(email='client@test.com', role='client')
        user.set_password('password123')
        db_session.session.add(user)
        db_session.session.commit()
        token = create_access_token(
            identity=str(user.id),
            additional_claims={'role': 'client'}
        )
    return token


@pytest.fixture(scope='function')
def sample_service(app, db_session):
    """Create a real service in the test database that tests can reference."""
    with app.app_context():
        service = Service(
            name='Haircut',
            duration_mins=60,
            price=45.00,
            is_active=True
        )
        db_session.session.add(service)
        db_session.session.commit()
        return service.id 