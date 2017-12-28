from flask import Flask, redirect, url_for, session, request, render_template
from datetime import datetime
import socket
import json


def to_bits(data):
    data = json.dumps(data)
    return data.encode('utf-8')


def to_json(data):
    data = data.decode('utf-8')
    return json.loads(data)


app = Flask(__name__)

max_size = 1000

# addressUsers = ('192.168.2.102', 8000)
addressUsers = ('localhost', 8005)
print('Starting the users at ', datetime.now())
users = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
users.connect(addressUsers)

# addressServer = ('192.168.2.101', 8000)
addressServer = ('localhost', 8000)
print('Starting the server at ', datetime.now())
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect(addressServer)


@app.route('/', methods=['GET', 'POST'])
def login(name=None):
    if request.method == 'GET':
        return render_template('index.html', name=name)
    else:
        pm_data = {}
        pm = {}
        pm['number'] = request.form['username']
        pm['password'] = request.form['password']
        pm_data["data"]= pm
        pm_data['operation'] = "logIn"
        pm_data = to_bits(pm_data)
        users.send(pm_data)
        print('Message send to users at', datetime.now())
        data = users.recv(max_size)
        print('Message receive from users at', datetime.now())
        data = to_json(data)
        if data['result'] == "denied":
            return redirect(url_for('index'))
        else:
            pm_total = {}
            pm_total['source'] = "ui"
            pm_total['destination'] = "enteties"
            pm_total['operation'] = "getUserIDs"
            temp = {}
            temp['number'] = request.form['username']
            pm_total['data'] = temp
            pm_total = to_bits(pm_total)
            server.send(pm_total)
            print('Message send to server at', datetime.now())
            pm_total = server.recv(max_size)
            print('Message receive from server at', datetime.now())
            pm_total = to_json(pm_total)
            result = pm_total['result']
            return result
            session['id'] = result["userid"]
            if 'studentid' in result:
                session['role'] = result['studentid']
            elif 'employeeid' in result:
                session['role'] = result['employeeid']
            else:
                session['role'] = result['teacherid']
            # return redirect(url_for('dashboard'))


@app.route('/dashboard')
def dashboard(name=None):
    return render_template('dashboard.html', name=name)


@app.route('/schedule',  methods=['GET', 'POST'])
def schedule():
    pm_total = {}
    pm_total['source'] = "ui"
    pm_total['destination'] = "timetables"
    pm_data = {}
    if request.method == 'GET':
        pm_total['operation'] = "getTimetableDay"
        now = datetime.now()
        pm_data['day'] = now.day
        pm_data['month'] = now.month
        pm_data['year'] = now.year
    else:
        pm_total['operation'] = "getTimetableRoom"
        pm_data['day'] = request.form['day']
        pm_data['month'] = request.form['month']
        pm_data['year'] = request.form['year']
        pm_data['room'] = request.form['room']
    pm_data['userid'] = session['id']
    pm_total['data'] = pm_data
    pm_total = to_bits(pm_total)
    server.send(pm_total)
    print('Message send to server at', datetime.now())
    pm_data = server.recv(max_size)
    print('Message receive from server at', datetime.now())
    pm_data = to_json(pm_data)
    return pm_data
    # return render_template('schedule.html', schedule=pm_data['data'])


@app.route('/bookRoom',  methods=['GET', 'POST'])
def book_room():
    if request.method == 'GET':
        pm_total = {}
        pm_total['source'] = "ui"
        pm_total['destination'] = "enteties"
        pm_total['operation'] = "getallrooms"
        pm_total = to_bits(pm_total)
        server.send(pm_total)
        print('Message send to server at', datetime.now())
        data = server.recv(max_size)
        print('Message receive from server at', datetime.now())
        data = to_json(data)
        return data
        # return render_template('bookRoom.html', data=data)
    else:
        pm_total = {}
        pm_total['source'] = "ui"
        pm_total['destination'] = "timetables"
        pm_total['operation'] = "bookRoom"
        pm_data = {}
        pm_data['userid'] = session['id']
        pm_data['room'] = request.form['room']
        pm_data['startTime'] = request.form['startTime']
        pm_data['endTime'] = request.form['endTime']
        pm_data['day'] = request.form['day']
        pm_data['mouth'] = request.form['mouth']
        pm_data['year'] = request.form['year']
        pm_total['data'] = pm_data
        pm_total = to_bits(pm_total)
        server.send(pm_total)
        print('Message send to server at', datetime.now())
        data = server.recv(max_size)
        print('Message receive from server at', datetime.now())
        data = to_json(data)
        return data
        # return render_template('dashboard.html', data=data['result'])


@app.route('/settings', methods=['GET', 'POST'])
def settings(name=None):
    if request.method == 'GET':
        return render_template('settings.html', name=name)
    else:
        pm_total = {}
        pm_total['source'] = "ui"
        pm_total['destination'] = "users"
        pm_total['operation'] = "settings"
        pm_data = {}
        pm_data['userid'] = session['id']
        pm_data['name'] = request.form['name']
        pm_data['email'] = request.form['email']
        pm_data['phone'] = request.form['phone']
        pm_data['number'] = request.form['number']
        pm_data['password'] = request.form['password']
        pm_total['data'] = pm_data
        pm_total = to_bits(pm_total)
        server.send(pm_total)
        print('Message send to server at', datetime.now())
        pm_data = server.recv(max_size)
        print('Message receive from server at', datetime.now())
        pm_data = to_json(pm_data)
        if pm_data['result'] == "sucess":
            users.send(pm_total)
            print('Message send to users at', datetime.now())
            #pm_data = users.recv(max_size)
            print('Message receive from users at', datetime.now())
            #pm_data = to_json(pm_data)
            if pm_data['result'] == "sucess":
                # return render_template('settings.html', data=pm_data['result'])
                return pm_data
        # return render_template('settings.html', data=pm_data['result'])
        return pm_data


@app.route('/signUp', methods=['GET', 'POST'])
def sign_up(name=None):
    if request.method == 'GET':
        return render_template('signUp.html', name=name)
    else:
        pm_total = {}
        pm_total['source'] = "ui"
        pm_total['destination'] = "enteties"
        if request.form['role'] == "Student":
            pm_total['operation'] = "registerStudent"
        elif request.form['role'] == "Teacher":
            pm_total['operation'] = "registerTeacher"
        else:
            pm_total['operation'] = "registerEmployee"
        pm_data = {}
        pm_data['name'] = request.form['name']
        pm_data['email'] = request.form['email']
        pm_data['phone'] = request.form['phone']
        pm_data['number'] = request.form['number']
        pm_data['password'] = request.form['password']
        pm_total['data'] = pm_data
        pm_total = to_bits(pm_total)
        users.send(pm_total)
        print('Message send to users at', datetime.now())
        server.send(pm_total)
        print('Message send to server at', datetime.now())
        user_data = users.recv(max_size)
        print('Message receive from users at', datetime.now())
        server_data = server.recv(max_size)
        print('Message receive from server at', datetime.now())
        data = to_json(user_data)
        if data['result'] == "sucess":
            data = to_json(server_data)
            result = pm_total['result']
            session['id'] = result["userid"]
            if 'studentid' in result:
                session['role'] = result['studentid']
            elif 'employeeid' in result:
                session['role'] = result['employeeid']
            else:
                session['role'] = result['teacherid']
            return data
            # return render_template('dashboard.html', data=data['result'])
        return data
        # return render_template('dashboard.html', data=data['result'])


app.secret_key = 'secret!'

