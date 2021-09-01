from datetime import datetime

from sqlalchemy import text

from application.database import db


class Document(db.Model):
    __tablename__ = 'document'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    link = db.Column(db.String, nullable=False)
    available = db.Column(db.Boolean, default=True, server_default=text('true'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, server_default=text('CURRENT_TIMESTAMP'),
                           onupdate=text('CURRENT_TIMESTAMP'))