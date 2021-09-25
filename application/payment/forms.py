from flask_wtf import FlaskForm
from wtforms import IntegerField
from wtforms.validators import DataRequired, NumberRange


class Payment(FlaskForm):
    class Meta:
        csrf = False

    user_id = IntegerField('User ID', validators=[DataRequired()])
    amount = IntegerField('Amount of payment', validators=[NumberRange(min=100, max=15000)])
