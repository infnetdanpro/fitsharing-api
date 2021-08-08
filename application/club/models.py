import datetime
import enum

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
    lat = db.Column(db.Float, unique=False, nullable=False, server_default='0.0')   # широта
    lng = db.Column(db.Float, unique=False, nullable=False, server_default='0.0')   # долгота
    about = db.Column(db.String(1024), unique=False, nullable=True)
    enabled = db.Column(db.Boolean, unique=False, nullable=True, default=True, server_default='true')
    point = db.Column(Geometry('point'))    # SRID 4326 - longitude and latitude
    images = relationship('ClubGallery')
    work_hours = relationship('ClubWorkSchedule')

    def get_price_per_minute(self):
        price = db.session.execute("""
            SELECT price FROM club_service WHERE club_id = :club_id AND service_type = 'main'
        """, params={'club_id': self.id}).fetchall()
        if not price:
            return 0

        return price[0][0]

class ClubGallery(db.Model):
    __tablename__ = 'club_gallery'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    image = db.Column(db.String)
    sequence = db.Column(db.Integer, default=0)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow(), server_default=text('CURRENT_TIMESTAMP'))


class StrEnum(str, enum.Enum):
    def __new__(cls, *args):
        for arg in args:
            if not isinstance(arg, (str, enum.auto)):
                raise TypeError(
                    "Values of StrEnums must be strings: {} is a {}".format(
                        repr(arg), type(arg)
                    )
                )
        return super().__new__(cls, *args)

    def __str__(self):
        return self.value

    # The first argument to this function is documented to be the name of the
    # enum member, not `self`:
    # https://docs.python.org/3.6/library/enum.html#using-automatic-values
    def _generate_next_value_(name, *_):
        return name


class Days(StrEnum):
    monday = 'monday'
    tuesday = 'tuesday'
    wednesday = 'wednesday'
    thursday = 'thursday'
    friday = 'friday'
    saturday = 'saturday'
    sunday = 'sunday'


days_order = ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')


class ClubWorkSchedule(db.Model):
    __tablename__ = 'club_work_schedules'
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Enum(Days), nullable=False)
    work_hours = db.Column(db.String, nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)

    def __str__(self):
        return str(self.day.value)

    def __repr__(self):
        return str(self.day.value)


class Service(db.Model):
    __tablename__ = 'service'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    about = db.Column(db.String(1024), unique=False, nullable=False)
    enabled = db.Column(db.Boolean, unique=False, nullable=True, default=True, server_default='true')


class ServiceType(StrEnum):
    main = 'main'
    additional = 'additional'


class ClubService(db.Model):
    __tablename__ = 'club_service'

    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
    club = relationship(Club)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    service = relationship(Service)
    enabled = db.Column(db.Boolean, nullable=True, default=True, server_default='true')
    price = db.Column(db.Float, nullable=True)
    service_type = db.Column(db.Enum(ServiceType), nullable=True, default='additional', server_default='additional')
