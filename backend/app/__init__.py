import logging

from flask import Flask
from flask_cors import CORS

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)


def create_app():
    app = Flask(__name__)
    from app.routes import delete_bp, detect_bp, main_bp, upload_bp

    # Register blueprints or routes
    app.register_blueprint(main_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(detect_bp)
    app.register_blueprint(delete_bp)
    CORS(app, resources={r'/*': {'origins': '*'}})

    return app
