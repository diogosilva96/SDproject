import socket
import time
import json

#PARA TESTES NA COMUNICAÇÃO
address = ('localhost',8002)
max_size = 1024
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(address)
while True:
    print("Type operation")
    inf = input()
    if inf == "view":
        rid = str(1)
        day = str(1)
        month = str(12)
        year = str(2019)
        message = '{"source":"ui" ,"destination":"timetables" ,"operation": "getTimetableRoom", "data":{"roomid":'+rid+',"day":'+ day +',"month":'+month+',"year":'+year+'}}'
        message = message.encode('utf-8')
       # print("Mensagem enviada: ",message)
        client.sendall(message)
    if inf == "gettimetableday":
        userid = str(1)
        day = str(1)
        month = str(12)
        year = str(2019)
        message = '{"source":"ui" ,"destination":"timetables" ,"operation": "getTimetableDay", "data":{"userid":'+userid+',"day":'+ day +',"month":'+month+',"year":'+year+'}}'
        message = message.encode('utf-8')
       # print("Mensagem enviada: ",message)
        client.sendall(message)
    if inf == "access":
        uid = str(1)
        rid = str(1)
        t = time.localtime()
        day = str(t.tm_mday)
        month = str(t.tm_mon)
        year = str(t.tm_year)
        th = str(t.tm_hour)
        tm = str(t.tm_min)
        ts = str(t.tm_sec)
        message = '{"source": "ui" ,"destination": "timetables" ,"operation":"access", "data":{"userid":' + str(uid) + ' ,"roomid":' + str(rid) + ',"day": ' + day + ' ,"month":' + month + ' ,"year":' + year + ' ,"hours":' + th + ' ,"minutes":' + tm + ' ,"seconds":' + ts + '}}'
        message = message.encode('utf-8')
        #print("Mensagem enviada: ",message)
        client.sendall(message)
    if inf == "book":
        day = '1'
        month = '12'
        year = '2019'
        id_teacher = '2'
        id_room = '1'
        startHour = '23'
        endHour = '24'
        message = '{"source": "cardreader" ,"destination": "timetables" ,"operation":"bookRoom", "data":{"userid":'+ id_teacher + ', "roomid":'+ id_room+' ,"day":'+day+' ,"month":'+month+' ,"year":'+year+' ,"startHour":'+startHour+' ,"endHour":'+endHour+'}}'
        message = message.encode('utf-8')
        client.sendall(message)
    #client.close()
    #print("socket closed")
    data = client.recv(max_size)
    if data:
        _data=data.decode('utf-8')
        print("Mensagem recebida: ",_data)
        _data = json.loads(_data)
        if _data['operation']=="access":
            print("Pode aceder: ",_data['result'])
        if _data['operation']=="book":
            print(_data)




