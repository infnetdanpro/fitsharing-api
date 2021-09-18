from functools import wraps

from flask import url_for
from flask_login import current_user
from werkzeug.utils import redirect


def non_auth(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        if current_user.is_authenticated:
            return redirect(url_for('club_admin.main_view'), code=302)
        return f(*args, **kwds)

    return wrapper


def auth_only(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        if not current_user.is_authenticated:
            return redirect(url_for('club_admin.login_view'), code=302)
        return f(*args, **kwds)

    return wrapper
