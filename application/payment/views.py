import datetime
import logging
import uuid
from distutils.command.config import config
from uuid import uuid4

from flask import render_template, request, flash, jsonify, url_for

from application import config
from application.database import db
from application.models.payment.models import Invoice
from application.models.user.models import User
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
    context: dict = {}
    title: str = 'Страница пополнения баланса'
    context.update(title=title)
    any_errors: bool = False

    try:
        uuid.UUID(invoice_uuid)
    except ValueError:
        any_errors = True
        flash('Неверный или истекший счет на оплату', 'error')

    user_invoice = db.session.query(Invoice)\
        .filter(Invoice.invoice_uuid == invoice_uuid)\
        .filter(Invoice.expired_at >= datetime.datetime.utcnow())\
        .first()

    if not user_invoice:
        any_errors = True
        flash('Счет на оплату не найден или он истек', 'error')

    # get active user:
    if user_invoice:
        user = db.session.query(User.email)\
            .filter(User.id == user_invoice.user_id)\
            .filter(User.enabled.is_(True))\
            .first()
        if not user:
            any_errors = True
            flash('Данному пользователь доступ к пополнению баланса запрещен. '
                  'Обратитесь в техподдержку. Код ошибки: #8827Pay', 'error')
        else:
            context.update(user_email=user.email)

    context.update(any_errors=any_errors)

    if user_invoice:
        # Формулы комиссии: https://yoomoney.ru/docs/payment-buttons/using-api/forms
        yoomoney_a = 0.005
        yoomoney_amount = round(user_invoice.amount - user_invoice.amount * (yoomoney_a / (1 + yoomoney_a)), 2)

        yoomoney_b = 0.02
        yoomoney_card_amount = round(user_invoice.amount * (1 - yoomoney_b), 2)

        context.update(invoice_uuid=user_invoice.invoice_uuid)
        context.update(amount=user_invoice.amount)
        context.update(wallet_id=config.YOOMONEY_WALLET_ID)
        context.update(yoomoney_amount=yoomoney_amount)
        context.update(yoomoney_card_amount=yoomoney_card_amount)
        # context.update(success_url=url_for('payment.invoice_payment_view', invoice_uuid=invoice_uuid) + '?success=True')
    return render_template('payment/form.html', **context)

