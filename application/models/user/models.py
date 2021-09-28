import logging
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import relationship

from application.database import db


logger = logging.getLogger('user_models')

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
    created_at = db.Column(db.DateTime, default=datetime.now, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = db.Column(db.DateTime, default=datetime.now, server_default=text('CURRENT_TIMESTAMP'),
                           onupdate=text('CURRENT_TIMESTAMP'))
    verified = relationship('VerifiedUsersByClub', back_populates='user_verify')
    balance = relationship('UserBalance')

    def __repr__(self):
        return f'<User {self.username}. ID: {self.id}>'


class VerifiedUsersByClub(db.Model):
    """
    Which club verified users data
    """
    __tablename__ = 'verified_user_by_club'

    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
    club = relationship('Club')
    verified_by_club_user_id = db.Column(db.Integer, db.ForeignKey('club_user.id'))
    verified_by_club_user = relationship('ClubUser')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_verify = relationship(User, back_populates='verified')     # this is real user
    created_at = db.Column(db.DateTime, default=datetime.now, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = db.Column(db.DateTime, default=datetime.now, server_default=text('CURRENT_TIMESTAMP'),
                           onupdate=text('CURRENT_TIMESTAMP'))
    complete = db.Column(db.Boolean, default=False)


class ForgotPassword(db.Model):
    __tablename__ = 'forgot_password'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reset_code = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, server_default=text('CURRENT_TIMESTAMP'))


class UserBalance(db.Model):
    __tablename__ = 'user_balance'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    amount = db.Column(db.Integer, default=0, server_default=text('0'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, server_default=text('CURRENT_TIMESTAMP'), onupdate=datetime.utcnow)

    @classmethod
    def update(cls, user_id: int, amount: int) -> int:
        if amount <= 0:
            return

        user_balance = cls.get_or_create(user_id=user_id)

        try:
            user_balance.amount += amount
            db.session.commit()
            print('-----------')
            print(user_balance.amount)
            print('-----------')
        except Exception as e:
            logger.exception(
                'Promblem with update user balance: user_id=%s, amount=%s. Text error: %s',
                user_id,
                amount,
                str(e)
            )
            db.session.rollback()

        return user_balance.amount

    @classmethod
    def get_or_create(cls, user_id: int):
        balance_obj = db.session.query(cls).filter(cls.user_id == user_id).first()

        if not balance_obj:
            balance_obj = cls(user_id=user_id, amount=0)
            try:
                db.session.add(balance_obj)
                db.session.commit()
            except Exception as e:
                db.session.rollback()

        return balance_obj
