from datetime import datetime

from sqlalchemy import text

from application.models.utils import StrEnum
from application.database import db


class NotificationType(StrEnum):
    info = 'info'
    warning = 'warning'
    error = 'error'


class Notification(db.Model):
    __tablename__ = 'notification'

    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=True)
    club_user_id = db.Column(db.Integer, db.ForeignKey('club_user.id'), nullable=True)  # FOR WHO IF NEEDED!
    notify_type = db.Column(db.Enum(NotificationType), nullable=False)
    notify_text = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow,
                           server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))


class NotificationView(db.Model):
    __tablename__ = 'notification_view'

    id = db.Column(db.Integer, primary_key=True)
    notification_id = db.Column(db.Integer, db.ForeignKey('notification.id'), nullable=False)
    club_user_id = db.Column(db.Integer, db.ForeignKey('club_user.id'), nullable=True)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow,
                          server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))
