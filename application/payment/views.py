import datetime
import logging
import uuid
from uuid import uuid4

from flask import render_template, request, flash, redirect, url_for, jsonify

from application.database import db
from application.models.payment.models import Invoice
from application.payment.forms import Payment

logger = logging.getLogger('payment')


def form_view():
    context = {}
    title = 'Страница пополнения баланса'
    context.update(title=title)

    payment_data: dict = request.get_json()
    form_wtf = Payment(**payment_data)

    if form_wtf.validate():
        invoice = Invoice(
            user_id=form_wtf.user_id.data,
            amount=form_wtf.amount.data,
            expired_at=datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
        )
        try:
            db.session.add(invoice)
            db.session.commit()
            return jsonify({'invoice_uuid': invoice.invoice_uuid})
        except Exception as e:
            flash('Ошибка создания платежа, пожалуйста, обратитесь в техподдержку! Код ошибки: #3139PAY')
            logger.exception('Something wrong with adding an invoice: %s', str(e))
    for error in form_wtf.errors:
        flash(form_wtf.errors[error][0], 'error')

    context.update(form_wtf=form_wtf)
    return render_template('payment/form.html', **context)


def invoice_payment_view(invoice_uuid: uuid4):
    """Process created invoice"""
    try:
        uuid.UUID(invoice_uuid)
    except ValueError:
        flash('Wrong Invoice ID', 'error')

    user_invoice = db.session.query(Invoice)\
        .filter(Invoice.invoice_uuid == invoice_uuid)\
        .filter(Invoice.expired_at <= datetime.datetime.utcnow())\
        .first()

    if not user_invoice:
        return str('Счет на оплату не найден или он истек')

    return str(invoice_uuid)
