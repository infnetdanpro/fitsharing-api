import logging
import string

from email_validator import validate_email, EmailNotValidError
from flask import render_template, url_for, flash
from flask import request
from flask_login import login_user, current_user, logout_user
from werkzeug.utils import redirect

from application.club_admin.forms import RegisterForm, AuthForm
from application.club_admin.utils import non_auth
from application.database import db
# TODO: move this into main lib
from application.api.funcs.password import verify_password, hash_password
from application.models.club_user.models import ClubUser
from application.models.role.models import Role, ClubUserRole

from functools import wraps

logger = logging.getLogger(__name__)


def index_view():
    return redirect(url_for('club_admin.main_view' if current_user.is_authenticated else 'club_admin.login_view'), code=302)


@non_auth
def login_view():
    context = {
        'login_url': url_for('club_admin.login_view'),
        'club_register_url': url_for('club_admin.register_superadmin_view'),
    }
    form_wtf = AuthForm(request.form)
    form = dict(request.form)
    context.update(form=form, form_wtf=form_wtf)

    if request.method == 'POST' and form_wtf.validate():
        email, password, remember = form.get('email'), form.get('password'), form.get('remember')

        club_user = db.session \
            .query(ClubUser) \
            .filter(ClubUser.email == email) \
            .first()

        if club_user and verify_password(club_user.password, password):
            login_user(club_user, remember=remember == 'on')
            return redirect(url_for('club_admin.main_view'), code=302)
        else:
            flash('Пользователь не найден или пароль неверный!', 'error')

    for error in form_wtf.errors:
        flash(form_wtf.errors[error][0], 'error')

    return render_template('club_admin/login.html', **context)


@non_auth
def register_superadmin_view():
    context = {
        'login_url': url_for('club_admin.login_view'),
        'club_register_url': url_for('club_admin.register_superadmin_view'),
    }
    form_wtf = RegisterForm(request.form)
    form = dict(request.form)
    context.update(form=form, form_wtf=form_wtf)

    if request.method == 'POST' and form_wtf.validate():
        # TODO: move this validation to functions
        phone = form['phone'].strip('-').strip(' ').lstrip('+7').lstrip('8')
        if len(phone) != 10:
            flash('Длина мобильного номера телефона должна 10 символов. Пример: +79991112233', 'error')
            return render_template('club_admin/club_register.html', **context)

        if not phone.isdigit():
            # Expected: '1112223344'
            flash('Номер телефона должен содержать только цифры и знак "+". Пример: +79991112233', 'error')
            return render_template('club_admin/club_register.html', **context)

        for letter in string.ascii_lowercase:
            if letter in phone.lower():
                flash('Номер телефона должен содержать только цифры и знак "+". Пример: +79991112233', 'error')
                return render_template('club_admin/club_register.html', **context)

        if len(form['password']) < 7:
            flash('Длина пароля должна быть не менее 8 символов!', 'error')
            return render_template('club_admin/club_register.html', **context)

        if form['password'] != form['confirm_password']:
            flash('Пароли должны совпадать!', 'error')
            return render_template('club_admin/club_register.html', **context)

        email = form['email']
        try:
            valid = validate_email(email)
            email = valid.email
        except EmailNotValidError as e:
            flash('Введите валидный email!', 'error')
            return render_template('club_admin/club_register.html', **context)

        exists_club_user = db.session.query(ClubUser).filter(ClubUser.email == email).first()

        if exists_club_user:
            flash('Пользователь уже зарегистрирован, попробуйте войти с вашим email/паролем!', 'error')
            return render_template('club_admin/club_register.html', **context)

        try:
            club_user = ClubUser()
            club_user.fio = form['fio']
            club_user.password = hash_password(password=form['password'])
            club_user.phone = f'+7{phone}'
            club_user.email = email

            db.session.add(club_user)
            db.session.flush()

            club_admin_role = db.session.query(Role).filter(Role.name == 'club_superadmin').one()
            club_user_role = ClubUserRole()
            club_user_role.role_id = club_admin_role.id
            club_user_role.user_id = club_user.id

            db.session.add(club_user_role)
            db.session.commit()
            flash('Регистрация аккаунта прошла успешно', 'success')
            return redirect(url_for('club_admin.login_view'), code=302)
        except Exception as e:
            logger.exception('CLUB USER REGISTER ERROR: %s', str(e))
            flash('Возникла ошибка при регистрации', 'error')
            db.session.rollback()

    for error in form_wtf.errors:
        flash(form_wtf.errors[error][0], 'error')

    return render_template('club_admin/club_register.html', **context)


def logout_view():
    logout_user()
    return redirect(url_for('club_admin.login_view'), code=302)
