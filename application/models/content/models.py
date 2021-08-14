import datetime

from sqlalchemy import text

from application.database import db


class PublicPage(db.Model):
    __tablename__ = 'page'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String, nullable=False, unique=True)
    title = db.Column(db.String, nullable=True)
    h1 = db.Column(db.String, nullable=True)
    meta_description = db.Column(db.String, nullable=True)
    body = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, server_default=text('CURRENT_TIMESTAMP'),
                           onupdate=text('CURRENT_TIMESTAMP'))