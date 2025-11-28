from flask import Flask

def register_blueprints(app: Flask):
    """Register all blueprints with the Flask app."""

    with app.app_context():
        from api.routes import api_bp
        app.register_blueprint(api_bp)