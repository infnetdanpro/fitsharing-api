import datetime

from sqlalchemy import text
from sqlalchemy.orm import relationship
from application.database import db
from application.user.models import User
from application.club.models import Club, ClubService


class Order(db.Model):
    __tablename__ = 'order'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = relationship(User)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)
    club = relationship(Club)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow,
                           server_default=text('CURRENT_TIMESTAMP'))
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow,
                           server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))
    comment = db.Column(db.String(256), nullable=True)
    price = db.Column(db.Float, nullable=False)     # calculated
    time_to_come = db.Column(db.Integer, default=0, nullable=False)
    confirmation_code = db.Column(db.String(32), nullable=False)
    complete = db.Column(db.Boolean, default=False, server_default=text('false'))
    completed_at = db.Column(db.DateTime)
    confirmed_at = db.Column(db.DateTime)

    # Updated fields by client and club
    confirmed_client = db.Column(db.Boolean, default=False, nullable=False, server_default='false')     # boolean
    confirmed_club = db.Column(db.Boolean, default=False, nullable=False, server_default='false')     # boolean

    # For canceling orders
    canceled_by_client = db.Column(db.Boolean, default=False, nullable=False, server_default='false')
    canceled_by_club = db.Column(db.Boolean, default=False, nullable=False, server_default='false')
    is_active = db.Column(db.Boolean, default=False, nullable=False, server_default='false')


class OrderService(db.Model):
    __tablename__ = 'order_service'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    order = relationship(Order)
    club_service_id = db.Column(db.Integer, db.ForeignKey('club_service.id'))
    club_service = relationship(ClubService)