from flask import Flask, app, request, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from app.errors import register_error_handlers
from flask import redirect
import os
import uuid
import logging

logger = logging.getLogger(__name__)

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(test_config=None):
    app = Flask(__name__)
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        )

    database_url = os.getenv('DATABASE_URL')
    jwt_secret = os.getenv('JWT_SECRET_KEY')
    flask_env = os.getenv('FLASK_ENV', 'development')

    if not test_config:
        if not database_url:
            raise RuntimeError('DATABASE_URL environment variable is not set')
        if not jwt_secret:
            raise RuntimeError('JWT_SECRET_KEY environment variable is not set')

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = jwt_secret
    app.config['DEBUG'] = flask_env == 'development'


    if test_config:
        app.config.update(test_config)


    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Import models so Flask-Migrate can detect them
    from app.models.service import Service  # noqa: F401
    from app.models.client import Client   # noqa: F401
    from app.models.appointment import Appointment  # noqa: F401
    from app.models.user import User # noqa: F401

    # Register blueprints
    from app.routes.health import health_bp
    from app.routes.services import services_bp
    from app.routes.appointments import appointments_bp
    from app.routes.clients import clients_bp
    from app.routes.auth import auth_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(services_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(auth_bp)

    register_error_handlers(app)

    @app.before_request
    def before_request():
        g.request_id = str(uuid.uuid4())[:8]
        logger.info(
            f"[{g.request_id}] --> {request.method} {request.path}"
        )

    @app.after_request
    def after_request(response):
        logger.info(
            f"[{g.request_id}] <-- {request.method} {request.path} "
            f"{response.status_code}"
        )
        response.headers['X-Request-ID'] = g.request_id
        return response

    @app.route('/')
    def index():
        return redirect('/login')

    return app
