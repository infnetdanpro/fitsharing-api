from flask import Blueprint

from application.payment.views import *

bp = Blueprint(
    'payment',
    __name__,
    static_folder='static',
    template_folder='templates'
)

bp.add_url_rule('/', view_func=form_view, methods=['POST'])
bp.add_url_rule('/<invoice_uuid>', view_func=invoice_payment_view, methods=['GET'])
