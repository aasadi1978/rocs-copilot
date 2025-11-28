from backend.initialize_app.create_app import INITIALIZED_FLASK_APP, SQLALCHEMY_DB

with INITIALIZED_FLASK_APP.app_context():
    SQLALCHEMY_DB.create_all()

