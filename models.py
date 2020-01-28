'''from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tutors2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)'''
from sqlalchemy.sql import func
from app import db

Tutor_Goal = db.Table('Tutor_Goal',
                      db.Column('tutor_id', db.Integer, db.ForeignKey('Tutor.id')),
                      db.Column('goal_id', db.String, db.ForeignKey('Goal.id'))
                      )


class Tutor(db.Model):
    __tablename__ = 'Tutor'
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    name = db.Column(db.String, unique=True, nullable=False)
    about = db.Column(db.Text, default='text about tutor')
    rating = db.Column(db.Float, default=5.0)
    picture = db.Column(db.String, default='https://i.pravatar.cc/300?img=27')
    price = db.Column(db.Integer, default=1000)
    goals = db.relationship('Goal', secondary=Tutor_Goal, back_populates='tutors')
    schedules = db.relationship('Schedule', back_populates='tutor')
    messages = db.relationship('Message', back_populates='tutor')


class Goal(db.Model):
    __tablename__ = 'Goal'
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    icon = db.Column(db.String, nullable=False)
    ru_name = db.Column(db.String, nullable=False)
    requests = db.relationship('Request', back_populates='goal')
    tutors = db.relationship('Tutor', secondary=Tutor_Goal, back_populates='goals')


class Request(db.Model):
    __tablename__ = 'Request'
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    goal_id = db.Column(db.String, db.ForeignKey('Goal.id'))
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)
    _timenotch = db.Column(db.DateTime(timezone=True), default=func.now())
    goal = db.relationship('Goal', back_populates='requests')


class Schedule(db.Model):
    __tablename__ = 'Schedule'
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey('Tutor.id'))
    weekday = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    tutor = db.relationship('Tutor', back_populates='schedules')
    bookings = db.relationship('Booking', back_populates='schedule')


class Booking(db.Model):
    __tablename__ = 'Booking'
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('Schedule.id'))
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)
    _timenotch = db.Column(db.DateTime(timezone=True), default=func.now())
    schedule = db.relationship('Schedule', back_populates='bookings')


class Message(db.Model):
    __tablename__ = 'Message'
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey('Tutor.id'))
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)
    text = db.Column(db.String, nullable=False)
    _timenotch = db.Column(db.DateTime(timezone=True), default=func.now())
    tutor = db.relationship('Tutor', back_populates='messages')

