from application.database import db
from application.user.models import User
from application.funcs.password import verify_password


def authenticate(email, password):
    user = db.session.query(User).filter(User.email == email, User.enabled == 1).first()

    if not verify_password(user.password, password):
        return

    if user:
        return user


def identity(payload):
    user_id = payload['identity']
    return db.session.query(User).get(user_id)
