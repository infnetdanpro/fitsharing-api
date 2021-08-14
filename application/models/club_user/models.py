from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import text
from sqlalchemy.orm import relationship

from application.database import db
from application.models.club.models import Club
from application.models.role.models import ClubUserRole


class ClubUser(UserMixin, db.Model):
    __tablename__ = 'club_user'

    id = db.Column(db.Integer, primary_key=True)
    fio = db.Column(db.String(256), nullable=True)
    password = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(16), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    enabled = db.Column(db.Boolean, nullable=False, default=True, server_default='true')
    created_at = db.Column(db.DateTime, default=datetime.now, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = db.Column(db.DateTime, default=datetime.now, server_default=text('CURRENT_TIMESTAMP'),
                           onupdate=text('CURRENT_TIMESTAMP'))
    club_role = relationship(ClubUserRole, uselist=False)

    def __repr__(self):
        return f'<ClubUser {self.email}. ID: {self.id}>'


class ClubUserLog(db.Model):
    __tablename__ = 'club_user_log'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('club_user.id'))
    model_id = db.Column(db.Integer)
    model_type = db.Column(db.String)
    info = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.now, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = db.Column(db.DateTime, default=datetime.now, server_default=text('CURRENT_TIMESTAMP'),
                           onupdate=text('CURRENT_TIMESTAMP'))


class ClubUserAssociation(db.Model):
    __tablename__ = 'club_user_association'

    id = db.Column(db.Integer, primary_key=True)
    club_user_id = db.Column(db.Integer, db.ForeignKey('club_user.id'))
    club_user = relationship(ClubUser)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
    club = relationship(Club)
