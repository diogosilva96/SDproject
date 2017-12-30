import mysql.connector
import socket
import json
import threading
from datetime import datetime

conn = mysql.connector.connect(host="localhost",user='root', database='timetables')
cursor = conn.cursor(dictionary=True)

def checkAccessTeacher(day,month,year,accessHour,idroom,idteacher):
    accessHour
    canAccess = False
    accessHour=accessHour.split(":")
    query="SELECT DISTINCT periods.startHour, periods.endHour FROM periods,timetables WHERE timetables.day = %s AND timetables.month = %s AND timetables.year = %s AND timetables.id = periods.timetables_id AND periods.idroom = %s AND periods.idteacher = %s"
    cursor.execute(query, (day,month,year,idroom,idteacher))
    for period in cursor:
        sHour=period['startHour'].split(":")
        eHour=period['endHour'].split(":")
        if int(accessHour[0])>= int(sHour[0]) and int(accessHour[0])<=int(eHour[0]):
            if(int(accessHour[0])==int(sHour[0]) or int(accessHour[0])==int(eHour[0])):
                if(int(accessHour[1])>= int(sHour[1]) and int(accessHour[1])<int(eHour[1])):
                    canAccess = True
    return canAccess



def checkRoomAvailability(tid,rid,sHour,eHour):
    isOcupied = False
    isOcupiedHours = False
    isOcupiedMins = False
    sHour=sHour.split(":")
    eHour=eHour.split(":")
    query="SELECT startHour, endHour FROM periods WHERE timetables_id = %s AND idroom = %s"
    cursor.execute(query,(tid,rid))
    rows = cursor.fetchall()
    numrows = int(cursor.rowcount)
    if (numrows == 0):
        print("[Timetable Manager] No periods in that day")
    else:
        for row in rows:
            _sHour = row['startHour'].split(":")
            _eHour = row['endHour'].split(":")
            for ocupiedHours in range(int(_sHour[0]),int(_eHour[0])):
                if isOcupiedHours == True:
                    break
                for desiredHours in range(int(sHour[0]),int(eHour[0])):
                    #print(ocupiedHours,desiredHours)
                    if ocupiedHours==desiredHours:
                        isOcupiedHours = True
            if _sHour[1]>_eHour[1]:
                ocuRange= range(int(_eHour[1]), int(_sHour[1]))
            elif _sHour[1]<_eHour[1]:
                ocuRange=range(int(_sHour[1]), int(_eHour[1]))
            else:
                isOcupiedMins = True
            for ocupiedMinutes in ocuRange:
                if isOcupiedMins == True or isOcupiedHours ==False:
                    break
                else:
                    if sHour[1]>= eHour[1]:
                        desRange=range(int(eHour[1]),int(sHour[1]))
                    else:
                        desRange= range(int(sHour[1]),int(eHour[1]))
                    for desiredMinutes in desRange:
                        #print(ocupiedMinutes,desiredMinutes)
                        if ocupiedMinutes == desiredMinutes:
                            isOcupiedMins = True

        print (isOcupiedHours,isOcupiedMins)
    if (isOcupiedHours and isOcupiedMins) == True:
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
        print("[Timetable Manager] Room is not available to be booked.")
    return available



def getTimetableRoom(roomid,day,month,year):
    print(roomid,"-",day,"-",month,"-",year)
    query = ("SELECT periods.startHour, periods.endHour, periods.idteacher FROM timetables, periods "
             "WHERE  timetables.day=%s AND timetables.month = %s AND timetables.year = %s AND periods.timetables_id = timetables.id AND periods.idroom = %s ORDER BY periods.startHour DESC")
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
                    print(data)
                    data = data.decode('utf-8')
                    data = json.loads(data)
                    operation = data['operation']
                    print("[Timetable Manager] Message received: ", data)
                    if operation == "access":
                        hours=str(data['data']['hours']) + ":" + str(data['data']['minutes'])
                        canAccess = checkAccessTeacher(data['data']['day'],data['data']['month'],data['data']['year'],hours,data['data']['roomid'],data['data']['userid'])
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


