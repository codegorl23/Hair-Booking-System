from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)

    # Register blueprints
    from app.routes.health import health_bp
    app.register_blueprint(health_bp)
    
    return app
