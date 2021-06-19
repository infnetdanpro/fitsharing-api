import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
# SQLALCHEMY_DATABASE_URI = f'sqlite:///database.sqlite'
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'some-secret')

JWT_AUTH_USERNAME_KEY = 'email'
JWT_AUTH_URL_RULE = '/api/auth'
JWT_EXPIRATION_DELTA = os.environ.get('JWT_EXPIRATION_DELTA')
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

JWT_COOKIE_SECURE = os.environ.get('JWT_COOKIE_SECURE', False)
JWT_TOKEN_LOCATION = os.environ.get('JWT_TOKEN_LOCATION', 'cookies')
