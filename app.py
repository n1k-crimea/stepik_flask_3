# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, RadioField, SubmitField, HiddenField
from wtforms.validators import DataRequired
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tutors2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'wqeqrfdgvytrhgfbnfdgewtfgeryvsdferwow?!'
db = SQLAlchemy(app)

from models import Tutor, Tutor_Goal, Goal, Schedule, Booking, Request, Message


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


@app.route('/pick', methods=['POST', 'GET'])
def request_page():
    form_request = RequestForm()
    if form_request.validate_on_submit():
        request_goal = int(form_request.request_goal.data)
        request_client_name = form_request.request_client_name.data
        request_client_tel = form_request.request_client_tel.data
        request_new = Request(name=request_client_name, phone=request_client_tel, goal_id=request_goal)
        db.session.add(request_new)
        db.session.commit()
        return redirect(url_for('search_result_page'))
    return render_template('pick.html', form_request=form_request)


def get_data_tutors():
    with open('store/data.json', 'r', encoding='utf-8') as data_tutors:
        tmp_dict = json.loads(data_tutors.read())
    return (tmp_dict)


@app.context_processor
def pass_goals():
    week_days = {"mon": "понедельник", "tue": "вторник", "wed": "среда", "thu": "четверг", "fri": "пятница",
                 "sat": "суббота", "sun": "четверг"}
    goals = {goal.name: [goal.ru_name, goal.icon] for goal in db.session.query(Goal).all()}
    return dict(goals=goals, week_days=week_days)


@app.route('/')
def index_page():
    tutors_index = {}
    for tutor_row in db.session.query(Tutor).order_by(func.random()).limit(6):
        tutors_index[tutor_row.id] = {'name': tutor_row.name, 'about': tutor_row.about, 'picture': tutor_row.picture,
                                      'rating': tutor_row.rating, 'price': tutor_row.price}
    return render_template('index.html', tutors_index=tutors_index)


@app.route('/goals/<goal>/')
def goal_page(goal):
    query_tutor_goal = db.session.query(Tutor, Tutor_Goal, Goal).join(Tutor).join(Goal).filter(
        Goal.name == goal).order_by(Tutor.rating.desc()).all()
    tutors_goal = {}
    for tutor_row in query_tutor_goal:
        tutors_goal[tutor_row[0].id] = {'name': tutor_row[0].name, 'about': tutor_row[0].about,
                                        'picture': tutor_row[0].picture,
                                        'rating': tutor_row[0].rating, 'price': tutor_row[0].price}
    return render_template('goal.html', tutors_goal=tutors_goal, goal=goal)


@app.route('/profiles/<tutor_id>/')
def tutor_profile_page(tutor_id):
    tutor_row = db.session.query(Tutor).filter(Tutor.id == tutor_id).first()
    goals_rows = db.session.query(Tutor, Tutor_Goal, Goal).join(Tutor).join(Goal).filter(Tutor.id == tutor_id).all()
    schedule_rows = db.session.query(Schedule).filter(Schedule.tutor_id == tutor_id).order_by(Schedule.time).all()
    list_schedule_rows = [[row.id, row.weekday, row.time, row.enabled] for row in schedule_rows]
    tutor = {'id': tutor_row.id, 'name': tutor_row.name, 'about': tutor_row.about, 'picture': tutor_row.picture,
             'rating': tutor_row.rating,
             'price': tutor_row.price, 'goals': [goals_row[3].name for goals_row in goals_rows]}
    return render_template('profile.html', tutor=tutor, timetable=list_schedule_rows)


@app.route('/sent', methods=['POST', 'GET'])
def search_result_page():
    if request.form.get('request_client_name'):
        with open('store/request.json', 'r', encoding='utf-8') as request_file:
            tmp_dict = json.loads(request_file.read())
        count_request = str(len(tmp_dict) + 1)
        tmp_dict[count_request] = {'goal': request.form.get('request_goal'),
                                   'hours': request.form.get('request_hours'),
                                   'client_name': request.form.get('request_client_name'),
                                   'client_tel': request.form.get('request_client_tel')
                                   }
        with open('store/request.json', 'w', encoding='utf-8') as request_file:
            json.dump(tmp_dict, request_file, ensure_ascii=False, indent=4)
        return render_template('sent.html', request_data=tmp_dict[count_request])
    elif request.form.get('booking_client_name'):
        with open('store/booking.json', 'r', encoding='utf-8') as booking_file:
            tmp_dict = json.loads(booking_file.read())
        count_booking = str(len(tmp_dict) + 1)
        tmp_dict[count_booking] = {'tutor_id': request.form.get('booking_tutor_id'),
                                   'tutor_name': request.form.get('booking_tutor_name'),
                                   'day': request.form.get('booking_day'),
                                   'time': request.form.get('booking_time'),
                                   'client_name': request.form.get('booking_client_name'),
                                   'client_tel': request.form.get('booking_client_tel')
                                   }
        with open('store/booking.json', 'w', encoding='utf-8') as booking_file:
            json.dump(tmp_dict, booking_file, ensure_ascii=False, indent=4)
        return render_template('sent.html', booking_data=tmp_dict[count_booking])
    elif request.form.get('msg_client_name'):
        with open('store/message.json', 'r', encoding='utf-8') as message_file:
            tmp_dict = json.loads(message_file.read())
        count_message = str(len(tmp_dict) + 1)
        tmp_dict[count_message] = {'tutor_id': request.form.get('tutor_id'),
                                   'tutor_name': request.form.get('tutor_name'),
                                   'client_name': request.form.get('msg_client_name'),
                                   'client_tel': request.form.get('msg_client_tel'),
                                   'msg_text': request.form.get('msg_text')
                                   }
        with open('store/message.json', 'w', encoding='utf-8') as message_file:
            json.dump(tmp_dict, message_file, ensure_ascii=False, indent=4)
        return render_template('sent.html', tutor_name=tmp_dict[count_message]['tutor_name'],
                               client_name=tmp_dict[count_message]['client_name'])
    else:
        return 'ВСЕ НОРМ', 200


@app.route('/booking/<tutor_id_name>/<day_time>/<int:schedule_id>', methods=['POST', 'GET'])
def tutor_booking_page(tutor_id_name, day_time, schedule_id):
    tutor_id, tutor_name = tutor_id_name.split('--')
    day, time = day_time.split('--')
    form_booking = BookingForm()
    if form_booking.validate_on_submit():
        booking_client_name = form_booking.booking_client_name.data
        booking_client_tel = form_booking.booking_client_tel.data
        booking_tutor_id = form_booking.booking_tutor_id.data
        booking_tutor_name = form_booking.booking_tutor_name.data
        booking_day = form_booking.booking_day.data
        booking_time = form_booking.booking_time.data
        booking_new = Booking(name=booking_client_name, phone=booking_client_tel, schedule_id=schedule_id)
        db.session.add(booking_new)
        db.session.commit()
        return redirect(url_for('search_result_page'))

    booking_data = {'tutor_id': tutor_id, 'tutor_name': tutor_name, 'day': day, 'time': time}
    return render_template('booking.html', booking_data=booking_data, form_booking=form_booking)


@app.route('/message/<int:tutor_id>', methods=['POST', 'GET'])
def msg(tutor_id):
    form_msg = MsgForm()
    if form_msg.validate_on_submit():
        msg_tutor_id = form_msg.msg_tutor_id.data
        msg_client_name = form_msg.msg_client_name.data
        msg_client_tel = form_msg.msg_client_tel.data
        msg_text = form_msg.msg_text.data
        msg_new = Message(tutor_id=msg_tutor_id, name=msg_client_name, phone=msg_client_tel, text=msg_text)
        db.session.add(msg_new)
        db.session.commit()
        return redirect(url_for('search_result_page'))

    tutor_row = db.session.query(Tutor).filter(Tutor.id == tutor_id).first()
    tutor = {'id': tutor_row.id, 'name': tutor_row.name, 'picture': tutor_row.picture}
    return render_template('message.html', form_msg=form_msg, tutor=tutor)



