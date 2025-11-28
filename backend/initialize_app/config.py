from os import getenv
from pathlib import Path
import logging


class Config:
    
    data_dir = Path().resolve() / 'backend' / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)

    db_path = data_dir / 'messages.db'

    if not db_path.exists():
        logging.info(f"Database file not found. Will create new database at {db_path}")

    SQLALCHEMY_DATABASE_URI = getenv("DATABASE_URL") or f"sqlite:///{db_path}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
