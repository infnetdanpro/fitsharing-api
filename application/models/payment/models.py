import datetime
import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text

from application.database import db


class Invoice(db.Model):
    __tablename_ = 'invoices'

    id = db.Column(db.Integer, primary_key=True)
    invoice_uuid = db.Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Integer, default=100, nullable=False, server_default=text('100'))
    paid = db.Column(db.Boolean, default=False, nullable=False, server_default=text('false'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, server_default=text('CURRENT_TIMESTAMP'),
                           onupdate=datetime.datetime.utcnow)
    expired_at = db.Column(db.DateTime)
