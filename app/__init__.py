from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    # Import models so Flask-Migrate can detect them
    from app.models import service  # noqa: F401
    from app.models import client   # noqa: F401
    from app.models import appointment  # noqa: F401

    # Register blueprints
    from app.routes.health import health_bp
    from app.routes.services import services_bp
    from app.routes.appointments import appointments_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(services_bp)
    app.register_blueprint(appointments_bp)

    return app
