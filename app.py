# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from forms import BookingForm, RequestForm, MsgForm
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tutors2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'wqeqrfdgvytrhgfbnfdgewtfgeryvsdferwow?!'
db = SQLAlchemy(app)

from models import Tutor, Tutor_Goal, Goal, Schedule, Booking, Request, Message


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


@app.route('/profiles/<int:tutor_id>/')
def tutor_profile_page(tutor_id):
    tutor_row = db.session.query(Tutor).get_or_404(tutor_id)
    goals_rows = db.session.query(Tutor, Tutor_Goal, Goal).join(Tutor).join(Goal).filter(Tutor.id == tutor_id).all()
    schedule_rows = db.session.query(Schedule).filter(Schedule.tutor_id == tutor_id).order_by(Schedule.time).all()
    list_schedule_rows = [[row.id, row.weekday, row.time, row.enabled] for row in schedule_rows]
    tutor = {'id': tutor_row.id, 'name': tutor_row.name, 'about': tutor_row.about, 'picture': tutor_row.picture,
             'rating': tutor_row.rating,
             'price': tutor_row.price, 'goals': [goals_row[3].name for goals_row in goals_rows]}
    return render_template('profile.html', tutor=tutor, timetable=list_schedule_rows)


@app.route('/sent', methods=['GET'])
def search_result_page():
    return render_template('sent.html')


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


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
