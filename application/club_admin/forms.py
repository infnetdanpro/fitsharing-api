from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators, FloatField, BooleanField
from wtforms.fields.html5 import EmailField, DateTimeField
from wtforms.validators import DataRequired, Length, ValidationError


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


# def check_work_schedule(form, field):
#     work_hours = field.data.split('-')
#     open_time, close_time = work_hours[0], work_hours[1]
#     open_hour, open_minutes = int(open_time.split(':')[0]), int(open_time.split(':')[1])
#     close_hour, close_minutes = int(close_time.split(':')[0]), int(close_time.split(':')[1])
#
#     if (0 > open_hour > 24) or (0 > close_hour > 24):
#         raise ValidationError('Время открытия/закрытия должно быть в пределах 24 часов')
#     if (0 > open_minutes > 59) or (0 > close_minutes > 59):
#         raise ValidationError('Время открытия/закрытия должно быть в пределах 59 минут')

# class RegisterClubForm(FlaskForm):
#     club_name = StringField('club_name', validators=[DataRequired('Имя клуба обязательно'), Length(min=2, max=256)])
#     club_address = StringField('club_address', validators=[DataRequired('Адрес клуба обязателен'), Length(min=2, max=1024)])
#     club_phone = StringField('club_address', validators=[DataRequired('Телефон клуба обязателен'), Length(min=6, max=12)])
#     club_gps_lat = FloatField('club_gps_lat')
#     club_gps_lon = FloatField('club_gps_lon')
#     club_work_monday = StringField(validators=[DataRequired('Необходимо заполнить рабочее время в Понедельник')])

class VerificationUserForm(FlaskForm):
    firstname = StringField('firstname', validators=[DataRequired()])
    lastname = StringField('lastname', validators=[DataRequired()])
    email = EmailField('email', validators=[DataRequired()])
    phone = StringField('phone', validators=[DataRequired()])
    date_of_birth = DateTimeField('date_of_birth', validators=[DataRequired()], format='%Y-%m-%d')
