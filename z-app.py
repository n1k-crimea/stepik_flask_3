# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from random import shuffle
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tutors2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def get_data_tutors():
    with open('store/data.json', 'r', encoding='utf-8') as data_tutors:
        tmp_dict = json.loads(data_tutors.read())
    return (tmp_dict)


@app.context_processor
def pass_goals():
    goals = {"travel": ["для путешествий", '⛱'], "study": ["для учебы", '🏫'], "work": ["для работы", '🏢'],
             "relocate": ["для переезда", '🚜']}
    week_days = {"mon": "понедельник", "tue": "вторник", "wed": "среда", "thu": "четверг", "fri": "пятница",
                 "sat": "суббота", "sun": "четверг"}
    return dict(goals=goals, week_days=week_days)


@app.route('/')
def index_page():
    tmp_list = list(get_data_tutors().items())
    shuffle(tmp_list)
    return render_template('index.html', tutors_index=dict(tmp_list[6:]))


@app.route('/goals/<goal>/')
def goal_page(goal):
    tmp_list_id = {id: val for id, val in get_data_tutors().items() if goal in val['goals']}
    sorted_tmp_list_id = dict(sorted(tmp_list_id.items(), key=lambda item: item[1]['rating'], reverse=True))
    return render_template('goal.html', tutors_goal=sorted_tmp_list_id, goal=goal)


@app.route('/profiles/<tutor_id>/')
def tutor_profile_page(tutor_id):
    tutor = get_data_tutors()[tutor_id]
    tutor['id'] = tutor_id
    return render_template('profile.html', tutor=tutor)


@app.route('/sent', methods=['POST'])
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
        return 'Error!', 500


@app.route('/pick')
def request_page():
    return render_template('pick.html')


@app.route('/booking/<tutor_id>/<day>/<time>')
def tutor_booking_page(tutor_id, day, time):
    booking_data = {'tutor_id': tutor_id, 'tutor_name': get_data_tutors()[tutor_id]['name'], 'day': day, 'time': time}
    return render_template('booking.html', booking_data=booking_data)


@app.route('/message/<tutor_id>')
def msg(tutor_id):
    tutor = get_data_tutors()[tutor_id]
    tutor['id'] = tutor_id
    return render_template('message.html', tutor=tutor)


if __name__ == '__main__':
    app.run(debug=True)
