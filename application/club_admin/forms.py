from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    fio = StringField('fio', validators=[DataRequired(message='Поле ФИО обязательно!')])
    phone = StringField('phone', validators=[DataRequired(message='Необходимо ввести телефон!')])
    email = EmailField('email', validators=[DataRequired(message='Необходимо ввести email!')])
    password = PasswordField('password', validators=[
        DataRequired('Пароль обязателен!'),
        validators.EqualTo('confirm_password', message='Пароли должны совпадать')
    ])
    confirm_password = PasswordField('confirm_password', validators=[DataRequired()])


class AuthForm(FlaskForm):
    email = EmailField('email', validators=[DataRequired('Необходимо ввести email!')])
    password = PasswordField('password', validators=[DataRequired('Пароль обязателен!')])
