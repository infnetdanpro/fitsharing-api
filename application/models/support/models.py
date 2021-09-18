# import datetime
#
# from sqlalchemy import text
# from sqlalchemy.orm import relationship
#
# from application.database import db
#
#
# class Ticket(db.Model):
#     __tablename__ = 'tickets'
#
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String, unique=False, nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow(), server_default=text('CURRENT_TIMESTAMP'))
#     author_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     author_club_user_id = db.Column(db.Integer, db.ForeignKey('club_user.id'))
#     closed = db.Column(db.Boolean, default=False)
#
#
# class SupportTicket(db.Model):
#     __tablename__ = 'support_tickets'
#
#     id = db.Column(db.Integer, primary_key=True)
#     ticket_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     user = relationship('User')
#     club_user_id = db.Column(db.Integer, db.ForeignKey('club_user.id'))
#     club_user = relationship('ClubUser')
#     text = db.Column(db.String, nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow(), server_default=text('CURRENT_TIMESTAMP'))
