import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import warnings
from flask_cors import CORS
from initialize_app.config import Config


warnings.filterwarnings("ignore")

class CreateAPP:
    """Singleton class to create and manage the Flask app and Bcrypt instances."""
    _instance = None
    _initialized = False
    _app = None
    _bcrypt = None
    __sqlalchemy_db = None

    def __new__(cls):

        if cls._instance is None:

            cls._instance = super().__new__(cls)
            cls._instance._app = None
            cls._instance._bcrypt = None
            cls._instance._initialized = False
            cls._instance.__sqlalchemy_db = None
                    
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.create()

    def reset_instance(self):
        self._initialized = False
        self._app = None
        self._bcrypt = None

    def initialize_flask_app(self):
        if not self._app:
            self.create()
        return self._app

    def bcrypt(self):
        if not self._bcrypt:
            self.create()
        return self._bcrypt

    def get_config(self, config_key: str, default: str | None = None) -> str | None:
        
        if self.is_app_valid():
            self.create()
        
        try:
            conf = self._app.config.get(config_key)
        except Exception as e:
            logging.error(f"Error retrieving config '{config_key}': {e}")
            conf = None

        return conf if conf is not None else default

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def is_app_valid(self):
        return self._app is not None and self._bcrypt is not None and self._app.config.get('SQLALCHEMY_DATABASE_URI') is not None

    @property
    def sqlalchemy_db(self):
        return self.__sqlalchemy_db
    
    def create(self):

        if self._initialized and self.is_app_valid():
            logging.info(f"Flask app and Bcrypt instances already created.")
            return
        
        try:
            flask_app = Flask(__name__)

            flask_app.config.from_object(Config)
            # Enable CORS for the Flask app to handle cross-origin requests
            CORS(flask_app, resources={
                r"/api/*": {
                    "origins": ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
                    "methods": ["GET", "POST", "OPTIONS"],
                    "allow_headers": ["Content-Type"],
                    "supports_credentials": True
                },
                r"/rag/*": {
                    "origins": ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
                    "methods": ["GET", "POST", "OPTIONS"],
                    "allow_headers": ["Content-Type"],
                    "supports_credentials": True
                }
            })

            self.__sqlalchemy_db = SQLAlchemy()
            self.__sqlalchemy_db.init_app(flask_app)
            bcrypt = Bcrypt(flask_app)

            self._initialized = True
            self._app = flask_app
            self._bcrypt = bcrypt

            if self.is_app_valid():
                logging.info(f"Flask app and Bcrypt instances created successfully.")
            else:
                logging.critical(f"Flask app or Bcrypt instance is invalid after creation! Exiting the app with code 1.")
                self._app = None
                self._bcrypt = None
                self._initialized = False

        except Exception as e:
            logging.critical(
                f"Error at flask_app.py. The app could not be initialized! {str(e)}")
            self._app = None
            self._bcrypt = None
            self._initialized = False

app_isntance = CreateAPP.get_instance()
INITIALIZED_FLASK_APP = app_isntance.initialize_flask_app()
BCRYPT = app_isntance.bcrypt()
SQLALCHEMY_DB = app_isntance.sqlalchemy_db
