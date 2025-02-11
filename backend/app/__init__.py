from flask import Flask


def create_app():
    app = Flask(__name__)
    from app.routes import detect_bp, main_bp, upload_bp

    # Register blueprints or routes
    app.register_blueprint(main_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(detect_bp)

    return app
