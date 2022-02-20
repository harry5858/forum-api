import os
from dotenv import load_dotenv
from pathlib import Path
import datetime

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)

def create_sqlite_uri(db_name):
    return "sqlite:///" + os.path.join(BASE_DIR, db_name)

class BaseConfig:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=14)

class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = create_sqlite_uri("test.db")
    JWT_SECRET_KEY = os.getenv('FLASK_JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(hours=2)

config = {
    'testing': TestingConfig
}