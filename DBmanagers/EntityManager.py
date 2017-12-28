import mysql.connector
import socket
import json
import threading
from datetime import datetime

conn = mysql.connector.connect(host="localhost",user='root', database='enteties')
cursor = conn.cursor(dictionary=True)




def insertPerson(name,mail,phone,number):
    numberUsed=checkNumberUsed(number,"person")
    if numberUsed == False:
        add_person=("INSERT INTO persons "
                   "(name, email, phone, number) "
                   "VALUES (%s, %s, %s, %s)")

        data_person=(name,mail,phone,number)
        cursor.execute(add_person,data_person)
        lid = cursor.lastrowid
    else:
        lid ="used"
    return lid

def checkNumberUsed(number,type):
    if type == "person":
        numberUsed = False
        query = "SELECT persons.id FROM persons WHERE persons.number = %s"
        cursor.execute(query,(number,))
        cursor.fetchall()
        numrows = int(cursor.rowcount)
    elif type == "room":
        numberUsed = False
        query = "SELECT id FROM rooms WHERE number=%s"
        cursor.execute(query,(number,))
        cursor.fetchall()
        numrows = int(cursor.rowcount)
    if(numrows>0):
        numberUsed = True
    else:
        numberUsed = False
    return numberUsed

def insertTeacher(name,email,phone,number):
    teacherInserted = False
    person_id = insertPerson(name,email,phone,number)
    if person_id == "used":
        print("[Entity Manager] Teacher was not inserted, number already in use!")
        teacherInserted = False
    else:
        add_teacher = ("INSERT INTO teachers "
                    "(Person_id)"
                    "VALUES (%s)")
        data_teacher= (person_id,)
        cursor.execute(add_teacher,data_teacher)
        conn.commit()
        print("[Entity Manager] Teacher sucessfully added.")
        teacherInserted = True
    return teacherInserted

def getUserData(number): ## TERMINAR
    query="SELECT id,name,email,phone FROM persons WHERE number=%s"
    data_user = (number,)
    cursor.execute(query,data_user)
    userdata = cursor.fetchall()
    numrows = int(cursor.rowcount)
    if numrows==0:
        userdata = "denied"
    return userdata

def getUserIDs(number):
    foundRole = False
    query="SELECT persons.id AS userid,teachers.id AS teacherid FROM persons,teachers WHERE persons.number = %s AND persons.id = teachers.Person_id"
    data_teacher = (number,)
    cursor.execute(query,data_teacher)
    for teacher in cursor:
        foundRole = True
        useridinfo = teacher
    if (foundRole == False):
        query = "SELECT persons.id AS userid,students.id AS studentid FROM persons,students WHERE persons.number = %s AND persons.id = students.Person_id"
        data_teacher = (number,)
        cursor.execute(query, data_teacher)
        for student in cursor:
            foundRole = True
            useridinfo = student
    if (foundRole == False):
        query = "SELECT persons.id AS userid,employees.id AS employeeid FROM persons,employees WHERE persons.number = %s AND persons.id = employees.persons_id"
        data_employee = (number,)
        cursor.execute(query,data_employee)
        for employee in cursor:
            foundRole = True
            useridinfo = employee
    if (foundRole == False):
        useridinfo = "denied"
    return useridinfo



def insertEmployee(name,email,phone,number,role):
    employeeInserted = False
    person_id = insertPerson(name,email,phone,number)
    if person_id == "used":
        print("[Entity Manager] Employee was not inserted, number already in use.")
        employeeInserted = False
    else:
        add_employee = ("INSERT INTO employees (persons_id,role) VALUES (%s,%s)")
        data_employee=(person_id,role)
        cursor.execute(add_employee,data_employee)
        conn.commit()
        print("[Entity Manager] Employee sucessfully added.")
        employeeInserted = True
    return employeeInserted

def insertStudent(name,email,phone,number):
    studentInserted = False
    person_id = insertPerson(name, email, phone, number)
    if person_id == "used":
        print("[Entity Manager] Student was not inserted, number is already in use!")
        teacherInserted = False
    else:
        #adicionar course a students??
        add_student = ("INSERT INTO students "
                    "(Person_id)"
                    "VALUES (%s)")
        data_student= (person_id,)
        cursor.execute(add_student,data_student)
        conn.commit()
        print("[Entity Manager] Student sucessfully added")
        studentInserted = True
    return studentInserted

def editUserInfo(id,name,email,phone):
    queryupdate= "UPDATE persons SET name = %s, email = %s, phone =%s WHERE id = %s"
    cursor.execute(queryupdate, (name,email,phone,id))
    conn.commit()
    print("[Entity Manager] User information sucessfully edited.")#EFETUAR CHECKS se for inserido menos campos



def insertRoom(number,number_places,description):
    room_number_used = checkNumberUsed(number,"room")
    if room_number_used == False:
        add_room = ("INSERT INTO rooms "
                    "(number, number_places,description)"
                    "VALUES(%s,%s,%s)")
        data_room = (number,number_places,description)
        cursor.execute(add_room,data_room)
        conn.commit()
        room_inserted = True
    else:
        room_inserted = False
    return room_inserted

def checkAccessRoom(userid,roomid):
    canAccess = False
    query = "SELECT * FROM persons_has_rooms WHERE rooms_id =%s AND persons_id = %s"
    data_room = (roomid,userid)
    cursor.execute(query,data_room)
    cursor.fetchall()
    numrows = int(cursor.rowcount)
    if (numrows > 0):
        canAccess = True

    print(canAccess)
    return canAccess




def getAllRooms():
    query = ("SELECT id,number,number_places,description FROM rooms")
    cursor.execute(query)
    data = cursor.fetchall()
    return data


class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        print('[Entity Manager] Starting server at', datetime.now())
        print('[Entity Manager] Waiting for a client to call.')


    def listen(self):
        self.server.listen(5)
        while True:
            client, address = self.server.accept()
            print('[Entity Manager] Client called')
            #client.settimeout(60)
            threading.Thread(target = self.listenToClient,args = (client,address)).start()

    def listenToClient(self, client, address):
        max_size = 1024
        while True:
           # try:
                data = client.recv(max_size)
                if data:
                    data = data.decode('utf-8')
                    data = json.loads(data)
                    print("[Entity Manager] Message received: ", data)
                    operation = data['operation']
                    if operation == "registerTeacher":
                        teacherInserted=insertTeacher(data['data']['name'],data['data']['email'],data['data']['phone'],data['data']['number'])
                        if teacherInserted == True:
                            result = getUserIDs(data['data']['number'])
                        else:
                            result = 'denied'

                    if operation == "registerStudent":
                        studentInserted = insertStudent(data['data']['name'], data['data']['email'],data['data']['phone'], data['data']['number'])
                        if studentInserted == True:
                            result = getUserIDs(data['data']['number'])
                        else:
                            result = 'denied'
                    if operation == "registerEmployee":
                        employeeInserted = insertEmployee(data['data']['name'], data['data']['email'],data['data']['phone'], data['data']['number'], data['data']['role'])
                        if employeeInserted == True:
                            result = getUserIDs(data['data']['number'])
                        else:
                           result = 'denied'
                    if operation == "getUserIDs":
                        result=getUserIDs(data['data']['number'])

                    if operation == "editUserInfo":
                        editUserInfo(data['data']['userid'],data['data']['name'],data['data']['email'],data['data']['phone'])
                        result ='sucess'

                    if operation == "getUserData":
                        result = getUserData(data['data']['number'])
                    if operation == "insertRoom":
                        room_inserted = insertRoom(data['data']['number'],data['data']['numberplaces'],data['data']['description'])
                        if room_inserted == True:
                            result = "success"
                        else:
                            result = "denied"
                    if operation == "checkAccess":
                        canAccess = checkAccessRoom(data['data']['userid'],data['data']['roomid'])
                        result = canAccess
                    if operation == "getAllRooms":
                        data['data']={} # alterar
                        result = getAllRooms()

                    #operation get all users
                    #operation insert person room



                    message ={'source':data['destination'],'destination':data['source'],'operation':data['operation'],'data':data['data'],'result':result}
                    message = json.dumps(message)
                    message = message.encode('utf-8')
                    response = message
                    client.send(response)
                else:
                    response = "Wrong Operation"
                    response = response.encode('utf-8')
                    client.send(response)

           # except:
            #   client.close()
             #  print('socket closed')
             #  return False



if __name__ == "__main__":
    while True:
        ThreadedServer('localhost',8001).listen()




