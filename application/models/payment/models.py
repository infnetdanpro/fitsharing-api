import datetime
import uuid

from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import text
from sqlalchemy.orm import relationship

from application.database import db


class Invoice(db.Model):
    __tablename_ = 'invoices'

    id = db.Column(db.Integer, primary_key=True)
    invoice_uuid = db.Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, default=0, nullable=False, server_default=text('0'))
    paid = db.Column(db.Boolean, default=False, nullable=False, server_default=text('false'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, server_default=text('CURRENT_TIMESTAMP'),
                           onupdate=datetime.datetime.utcnow)
    expired_at = db.Column(db.DateTime)
    invoice_callback = relationship('InvoiceCallback')


class InvoiceCallback(db.Model):
    __tablename__ = 'invoices_callbacks'

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey(Invoice.id))
    sha1_hash = db.Column(db.String, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, server_default=text('CURRENT_TIMESTAMP'))
    is_valid = db.Column(db.Boolean, nullable=False)
    raw_data = db.Column(JSONB)
