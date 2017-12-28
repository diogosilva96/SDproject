import mysql.connector
import socket
import json
import threading
from datetime import datetime
import time

conn = mysql.connector.connect(host="localhost",user='root', database='timetables')
cursor = conn.cursor(dictionary=True)

def checkAccessTeacher(day,month,year,accessHour,idroom,idteacher):
    canAcess = False
    query="SELECT DISTINCT periods.startHour, periods.endHour FROM periods,timetables WHERE timetables.day = %s AND timetables.month = %s AND timetables.year = %s AND timetables.id = periods.timetables_id AND periods.idroom = %s AND periods.idteacher = %s"
    cursor.execute(query, (day,month,year,idroom,idteacher))
    for period in cursor:
        if int(accessHour) >= int(period['startHour']) and int(accessHour) < int(period['endHour']):
            canAcess = True
    return canAcess


#Selecionar sala apartir do dia, mes e ano
#Verificar o id da entidade no inicio
def checkRoomAvailability(tid,rid,sHour,eHour):
    isOcupied = False
    query="SELECT startHour, endHour FROM periods WHERE timetables_id = %s AND idroom = %s" #AND startHour = %s AND endHour = %s"
    cursor.execute(query,(tid,rid))
    rows = cursor.fetchall()
    numrows = int(cursor.rowcount)
    if (numrows == 0):
        print("No periods in that day")
    else:
        for row in rows:
            _sHour = int(row['startHour'])
            _eHour = int(row['endHour'])
            for ocupiedHours in range(_sHour,_eHour):
                for desiredHours in range(int(sHour),int(eHour)):
                    if ocupiedHours==desiredHours:
                        isOcupied = True

    return not isOcupied #Devolve se esta disponivel ou nao

def bookRoom(day,month,year,id_teacher,id_room,startHour,endHour):
    #Verifica se ja existe um timetable para tal dia
    query = ("SELECT id FROM timetables WHERE day = %s AND month = %s AND year = %s")
    cursor.execute(query, (day,month,year))
    row = cursor.fetchall()
    numrows = int(cursor.rowcount)
    if numrows == 0:
        #se nao existir insere no timetables
        add_timetables = ("INSERT INTO timetables "
                          "(day,month,year)"
                          "VALUES (%s, %s, %s)")

        data_timetables = (day, month, year)
        cursor.execute(add_timetables, data_timetables)
        lid = cursor.lastrowid
    else:
        #se existir vai buscar o id desse timetable
        query = ("SELECT id FROM timetables WHERE day = %s AND month = %s AND year = %s")
        cursor.execute(query, (day, month, year))
        for timetable in cursor:
            lid=timetable['id']
            print(lid)

    add_period = ("INSERT INTO periods "
                  "(startHour,endHour, idteacher , idroom , timetables_id)"
                  "VALUES (%s, %s, %s, %s, %s)")

    available = checkRoomAvailability(lid, id_room, startHour, endHour)
    #caso a sala esteja disponivel insere o periodo
    if available == True:
        data_period = (startHour,endHour,id_teacher,id_room, lid)
        cursor.execute(add_period,data_period)
        conn.commit()
        print("[Timetable Manager] Room booked with sucess.")
    #caso nao esteja envia msg de erro
    else:
        print("[Timetable Manager] Room is not available to be booked.")#mandar msg de erro
    return available



def getTimetableRoom(roomid,day,month,year):
    query = ("SELECT periods.startHour, periods.endHour FROM timetables, periods "
             "WHERE  timetables.day=%s AND timetables.month = %s AND timetables.year = %s AND periods.timetables_id = timetables.id AND periods.idroom = %s ")
    cursor.execute(query,(day,month,year,roomid))
    data = cursor.fetchall()
    return data

def getTimetableDay(userid,day,month,year):
    query = ("SELECT periods.startHour, periods.endHour,periods.idroom FROM timetables,periods "
             "WHERE timetables.day=%s AND timetables.month = %s AND timetables.year=%s AND  periods.timetables_id = timetables.id AND periods.idteacher = %s")
    cursor.execute(query, (day,month,year,userid))
    data = cursor.fetchall()
    return data

def DeleteTimetableTeacher(day,month,year,teacher_id):
    query="SELECT periods.id FROM periods,timetables WHERE periods.timetables_id = timetables.id AND periods.idteacher = %s AND timetables.day = %s AND timetables.month = %s AND timetables.year = %s"
    cursor.execute(query, (teacher_id,day,month,year))
    for x in cursor:
        for period_id in cursor:
            deletestmt = "DELETE FROM periods WHERE periods.id =%s"
            cursor.execute(deletestmt,(period_id))
            query = "SELECT periods.id FROM periods,timetables WHERE periods.timetables_id = timetables.id AND periods.idteacher = %s AND timetables.day = %s AND timetables.month = %s AND timetables.year = %s"
            cursor.execute(query, (teacher_id, day, month, year))
            print("delete do periodo do dia")
    conn.commit()



class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        print('[Timetable Manager] Starting server at', datetime.now())
        print('[Timetable Manager] Waiting for a client to call.')


    def listen(self):
        self.server.listen(5)
        while True:
            client, address = self.server.accept()
            print('[Timetable Manager] Client called')
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
                    operation = data['operation']
                    print("[Timetable Manager] Message received: ", data)
                    if operation == "access":
                        canAccess = checkAccessTeacher(data['data']['day'],data['data']['month'],data['data']['year'],data['data']['hours'],data['data']['roomid'],data['data']['userid'])
                        if canAccess == True:
                            print("[Timetable Manager] Acesso garantido na sala ",data['data']['roomid']," ao utilizador ",data['data']['userid'], " at ", datetime.now())
                            result = "success"
                        else:
                            print("[Timetable Manager] Acesso negado na sala ",data['data']['roomid']," ao utilizador ",data['data']['userid'], " at ", datetime.now())
                            result = "denied"

                    if operation== "getTimetableRoom":
                        result = getTimetableRoom(data['data']['roomid'],data['data']['day'],data['data']['month'],data['data']['year'])

                    if operation =="bookRoom":
                        available=bookRoom(data['data']['day'],data['data']['month'],data['data']['year'],data['data']['userid'],data['data']['roomid'],data['data']['startHour'],data['data']['endHour'])
                        if available == True:
                            result = 'success'
                        else:
                            result = 'denied'
                    if operation == "getTimetableDay":
                        result = getTimetableDay(data['data']['userid'],data['data']['day'],data['data']['month'],data['data']['year'])


                    message = {'source': data['destination'], 'destination': data['source'],
                               'operation': data['operation'],
                               'data': data['data'], 'result': result}
                    message = json.dumps(message)
                    message = message.encode('utf-8')
                    response = message
                    client.send(response)
                else:
                    response = "wrong operation"
                    response = response.encode('utf-8')
                    client.send(response)

           # except:
            #   client.close()
             #  print('socket closed')
             #  return False



if __name__ == "__main__":
    while True:
          ThreadedServer('localhost',8002).listen()


cursor.close()
conn.close()