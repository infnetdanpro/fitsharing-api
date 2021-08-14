from sqlalchemy.orm import relationship

from application.database import db


class Role(db.Model):
    __tablename__ = 'role'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    level = db.Column(db.Integer, default=0)


class UserRole(db.Model):
    __tablename__ = 'user_role'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))


class ClubUserRole(db.Model):
    __tablename__ = 'club_user_role'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('club_user.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    role = relationship(Role)

    def __repr__(self):
        return f'{self.role.name}:{self.role.level}'
