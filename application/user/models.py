from datetime import datetime

from sqlalchemy import text

from application.database import db


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    firstname = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(256), nullable=False)
    lastname = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(16), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    avatar = db.Column(db.String, nullable=True)
    date_of_birth = db.Column(db.Date, nullable=False)
    enabled = db.Column(db.Boolean, nullable=False, default=True, server_default='true')

    def __repr__(self):
        return f'<User {self.username}. ID: {self.id}>'


class ForgotPassword(db.Model):
    __tablename__ = 'forgot_password'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reset_code = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow(), server_default=text('CURRENT_TIMESTAMP'))
