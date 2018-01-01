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
        name = request.args.get('validation', '')
        return render_template('index.html', name=name)
    else:
        pm_data = {}
        pm = {}
        pm['number'] = request.form['username']
        pm['password'] = request.form['password']
        pm_data["data"] = pm
        pm_data['operation'] = "logIn"
        pm_data = to_bits(pm_data)
        users.send(pm_data)
        print('Message send to users at', datetime.now())
        data = users.recv(max_size)
        print('Message receive from users at', datetime.now())
        data = to_json(data)
        if data['result'] == "denied":
            return redirect(url_for('login', validation=False))
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
            session['users_id'] = data["userid"]
            session['enteties_id'] = result["userid"]
            if 'studentid' in result:
                session['role'] = "student"
            elif 'employeeid' in result:
                session['role'] = "employee"
            else:
                session['role'] = "teacher"
            print(session['role'])
            return redirect(url_for('dashboard', login=True))


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'role' in session:
        if request.method == 'POST':
            session.clear()
            return redirect(url_for('login'))
        if request.method == 'GET':
            name = request.args.get('validation', '')
            login = request.args.get('login', '')
            role = session['role']
            return render_template('dashboard.html', name=name, login=login, role=role)
    else:
        return redirect(url_for('login'))


@app.route('/schedule',  methods=['GET', 'POST'])
def schedule():
    if 'role' in session:
        pm_total = {}
        pm_total['source'] = "ui"
        pm_total['destination'] = "enteties"
        pm_total['operation'] = "getAllRooms"
        pm_total = to_bits(pm_total)
        server.send(pm_total)
        print('Message send to server at', datetime.now())
        data = server.recv(max_size)
        print('Message receive from server at', datetime.now())
        data = to_json(data)
        year = datetime.now().year
        rowspan = None
        if request.method == 'POST':
            pm_total = {}
            pm_total['source'] = "ui"
            pm_total['destination'] = "timetables"
            request_teachers = {}
            request_teachers['source'] = "ui"
            request_teachers['destination'] = "enteties"
            request_teachers['operation'] = "getTeachersInfo"
            request_teachers = to_bits(request_teachers)
            server.send(request_teachers)
            print('Message send to server at', datetime.now())
            request_teachers = server.recv(max_size)
            print('Message receive from server at', datetime.now())
            request_teachers = to_json(request_teachers)
            pm_total['operation'] = "getTimetableRoom"
            pm_data = {}
            pm_data['day'] = request.form['day']
            pm_data['month'] = request.form['month']
            pm_data['year'] = request.form['year']
            pm_data['roomid'] = request.form['room']
            pm_data['userid'] = session['enteties_id']
            pm_total['data'] = pm_data
            pm_total = to_bits(pm_total)
            server.send(pm_total)
            print('Message send to server at', datetime.now())
            pm_data = server.recv(max_size)
            print('Message receive from server at', datetime.now())
            pm_data = to_json(pm_data)
            print(pm_data)
            rowspan = {}
            schedules = pm_data['result']
            for n in schedules:
                start = n['startHour']
                end = n['endHour']
                valuestart = start.split(":")
                valueend = end.split(":")
                if valuestart[0] == valueend[0]:
                    rowspan[start] = 1
                else:
                    value = (int(valueend[0])-int(valuestart[0]))*2
                    if valuestart[1] != valueend[1]:
                        if valuestart[1] == "30":
                            value -= 1
                        else:
                            value += 1
                    rowspan[start] = value
        if request.method == 'GET':
            return render_template('schedule.html', schedule=None, year=year, rooms=data['result'], rowspan=None, teachers=None)
        else:
            return render_template('schedule.html', schedule=pm_data, year=year, rooms=data['result'], rowspan=rowspan, teachers=request_teachers['result'])
    else:
        return redirect(url_for('login'))


@app.route('/bookRoom',  methods=['GET', 'POST'])
def book_room():
    if 'role' in session:
        if request.method == 'GET':
            pm_total = {}
            pm_total['source'] = "ui"
            pm_total['destination'] = "enteties"
            pm_total['operation'] = "getAllRooms"
            pm_total = to_bits(pm_total)
            server.send(pm_total)
            print('Message send to server at', datetime.now())
            data = server.recv(max_size)
            print('Message receive from server at', datetime.now())
            data = to_json(data)
            print(data)
            year = datetime.now().year
            return render_template('bookRoom.html', data=data["result"], year=year)
        else:
            pm_total = {}
            pm_total['source'] = "ui"
            pm_total['destination'] = "timetables"
            pm_total['operation'] = "bookRoom"
            pm_data = {}
            pm_data['userid'] = session['enteties_id']
            pm_data['roomid'] = request.form['room']
            pm_data['startHour'] = request.form['startTime']
            pm_data['endHour'] = request.form['endTime']
            pm_data['day'] = request.form['day']
            pm_data['month'] = request.form['month']
            pm_data['year'] = request.form['year']
            pm_total['data'] = pm_data
            pm_total = to_bits(pm_total)
            print(pm_total)
            server.send(pm_total)
            print('Message send to server at', datetime.now())
            data = server.recv(max_size)
            print('Message receive from server at', datetime.now())
            data = to_json(data)
            if data['result'] == "success":
                return redirect(url_for('dashboard', validation=True))
            else:
                return redirect(url_for('dashboard', validation=False))
    else:
        return redirect(url_for('login'))


@app.route('/settings', methods=['GET', 'POST'])
def settings(name=None):
    if 'role' in session:
        if request.method == 'GET':
            return render_template('settings.html', name=name)
        else:
            pm_total = {}
            pm_total['source'] = "ui"
            pm_total['destination'] = "enteties"
            pm_total['operation'] = "editUserInfo"
            pm_data = {}
            pm_data['id'] = session['users_id']
            pm_data['userid'] = session['enteties_id']
            pm_data['name'] = request.form['name']
            pm_data['email'] = request.form['email']
            pm_data['phone'] = request.form['phone']
            pm_data['password'] = request.form['password']
            pm_total['data'] = pm_data
            pm_total = to_bits(pm_total)
            server.send(pm_total)
            print('Message send to server at', datetime.now())
            pm_data = server.recv(max_size)
            print('Message receive from server at', datetime.now())
            pm_data = to_json(pm_data)
            print(pm_data)
            if pm_data['result'] == "success":
                users.send(pm_total)
                print('Message send to users at', datetime.now())
                pm_data = users.recv(max_size)
                print(pm_data)
                print('Message receive from users at', datetime.now())
                pm_data = to_json(pm_data)
                if pm_data['result'] == "success":
                    return redirect(url_for('dashboard', validation=True))
                return redirect(url_for('dashboard', validation=False))
            return redirect(url_for('dashboard', validation=False))
    else:
        return redirect(url_for('login'))


@app.route('/signUp', methods=['GET', 'POST'])
def sign_up(name=None):
    if request.method == 'GET':
        return render_template('signUp.html', name=name)
    else:
        pm_total = {}
        pm_total['source'] = "ui"
        pm_total['destination'] = "enteties"
        print(request.form)
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
        print(pm_total)
        users.send(pm_total)
        print('Message send to users at', datetime.now())
        server.send(pm_total)
        print('Message send to server at', datetime.now())
        user_data = users.recv(max_size)
        print('Message receive from users at', datetime.now())
        server_data = server.recv(max_size)
        print('Message receive from server at', datetime.now())
        data = to_json(user_data)
        if data['result'] == "success":
            data = to_json(server_data)
            result = data['result']
            session['enteties_id'] = result["userid"]
            session['users_id'] = data["result"]["userid"]
            if 'studentid' in result:
                session['role'] = "student"
            elif 'employeeid' in result:
                session['role'] = "employee"
            else:
                session['role'] = "teacher"
            print(session['role'])
            return redirect(url_for('dashboard', login=True))
        return redirect(url_for('login', validation="false"))

app.secret_key = 'secret!'

