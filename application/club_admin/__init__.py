from flask import Blueprint

from application.club_admin.views.auth import *

bp = Blueprint(
    'club_admin',
    __name__,
    static_folder='static',
    template_folder='templates'
)

bp.add_url_rule('/login', view_func=login_view, methods=['GET', 'POST'])
bp.add_url_rule('/register', view_func=register_club_view, methods=['GET', 'POST'])
bp.add_url_rule('/logout', view_func=logout_view)
bp.add_url_rule('/blank', view_func=blank_page_view)