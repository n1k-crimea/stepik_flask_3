from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, RadioField, SubmitField, HiddenField
from wtforms.validators import DataRequired


class BookingForm(FlaskForm):
    booking_client_name = StringField('booking_client_name', validators=[DataRequired()])
    booking_client_tel = StringField('booking_client_tel', validators=[DataRequired()])
    submit = SubmitField('Записаться на пробный урок')
    booking_tutor_id = HiddenField('booking_tutor_id')
    booking_tutor_name = HiddenField('booking_tutor_name')
    booking_day = HiddenField('booking_day')
    booking_time = HiddenField('booking_time')


class RequestForm(FlaskForm):
    request_goal = RadioField('request_goal',
                              choices=[('1', 'Для путешествий'), ('2', 'Для учебы'), ('3', 'Для работы'),
                                       ('4', 'Для переезда')], validators=[DataRequired()])
    request_hours = RadioField('request_goal', choices=[('1-2', '1-2 часа в неделю'), ('3-5', '3-5 часов в неделю'),
                                                        ('5-7', '5-7 часов в неделю'), ('7-10', '7-10 часов в неделю')],
                               validators=[DataRequired()])
    request_client_name = StringField('request_client_name', validators=[DataRequired()])
    request_client_tel = StringField('request_client_tel', validators=[DataRequired()])
    submit = SubmitField('Найдите мне преподавателя')


class MsgForm(FlaskForm):
    msg_client_name = StringField('msg_client_name', validators=[DataRequired()])
    msg_client_tel = StringField('msg_client_tel', validators=[DataRequired()])
    msg_text = StringField('msg_text', validators=[DataRequired()])
    submit = SubmitField('Записаться на пробный урок')
    msg_tutor_id = HiddenField('msg_tutor_id')