from flask import Blueprint

from application.club_admin.views.auth import *
from application.club_admin.views.dashboard import *

bp = Blueprint(
    'club_admin',
    __name__,
    static_folder='static',
    template_folder='templates'
)

bp.add_url_rule('/', view_func=index_view)
bp.add_url_rule('/login', view_func=login_view, methods=['GET', 'POST'])
bp.add_url_rule('/register', view_func=register_club_view, methods=['GET', 'POST'])
bp.add_url_rule('/logout', view_func=logout_view)
bp.add_url_rule('/dashboard', view_func=main_view)
bp.add_url_rule('/club/add', view_func=add_club_view)
