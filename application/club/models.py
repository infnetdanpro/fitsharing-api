import datetime

from sqlalchemy import text
from sqlalchemy.orm import relationship
from application.database import db
from geoalchemy2 import Geometry

class Club(db.Model):
    __tablename__ = 'club'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=False, nullable=False)
    address = db.Column(db.String, unique=False, nullable=False)
    phone = db.Column(db.String, unique=False, nullable=False)
    lat = db.Column(db.Float, unique=False, nullable=False, server_default='0.0')
    lng = db.Column(db.Float, unique=False, nullable=False, server_default='0.0')
    about = db.Column(db.String(1024), unique=False, nullable=True)
    enabled = db.Column(db.Boolean, unique=False, nullable=True, default=True, server_default='true')
    point = db.Column(Geometry('point'))
    images = relationship('ClubGallery')


class ClubGallery(db.Model):
    __tablename__ = 'club_gallery'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    image = db.Column(db.String)
    sequence = db.Column(db.Integer, default=0)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow(), server_default=text('CURRENT_TIMESTAMP'))


class Service(db.Model):
    __tablename__ = 'service'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    about = db.Column(db.String(1024), unique=False, nullable=False)
    enabled = db.Column(db.Boolean, unique=False, nullable=True, default=True, server_default='true')


class ClubService(db.Model):
    __tablename__ = 'club_service'

    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
    club = relationship('Club')
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    service = relationship('Service')
    enabled = db.Column(db.Boolean, unique=False, nullable=True, default=True, server_default='true')
    price = db.Column(db.Float, unique=False, nullable=True)
