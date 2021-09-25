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
JWT_TOKEN_LOCATION = os.environ.get('JWT_TOKEN_LOCATION', ["headers", "cookies"])
JWT_REFRESH_TOKEN_EXPIRES = os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 86400)

SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
SENDGRID_SUBJECT = os.environ.get('SENDGRID_FROM_NAME', 'FitSharing Support')
SENDGRID_FROM_EMAIL = os.environ.get('SENDGRID_FROM_EMAIL', 'dan-pro352@ya.ru')

SENTRY_DSN = os.environ.get('SENTRY_DSN')
YOOMONEY_WALLET_ID = os.environ.get('YOOMONEY_WALLET_ID', '4100117196627468')