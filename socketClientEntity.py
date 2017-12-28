import socket
import json

#PARA TESTES NA COMUNICAÇÃO
address = ('localhost',8001)
max_size = 1024
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(address)
while True:
    print("Type Operation")
    inf = input()
    if inf == 'registert':
        name = 'John Teacher'
        email= 'john@email'
        phone = '9113232131231'
        number = '20201052'
        message = {'source': 'ui', 'destination': 'enteties', 'operation': 'registerTeacher',
                   'data': {'name':name,'email':email,'phone':phone,'number':number}}

    if inf == 'registers':
        name = 'John student XD new'
        email= 'john@email'
        phone = '911'
        number = '20201203241'
        message = {'source': 'ui', 'destination': 'enteties', 'operation': 'registerStudent',
                   'data': {'name':name,'email':email,'phone':phone,'number':number}}
    if inf == 'registere':
        name = 'John employee'
        email= 'john@emails'
        phone = '91123'
        number = '20201201'
        role = 'limpeza'
        message = {'source': 'ui', 'destination': 'enteties', 'operation': 'registerEmployee',
                   'data': {'name':name,'email':email,'phone':phone,'number':number, 'role':role}}
    if inf == 'getuserid':
        number = '20201052321'
        message = {'source': 'ui', 'destination':'enteties','operation':'getUserIDs',
                   'data':{'number':number}}
    if inf == 'getuserdata':
        number='2020106'
        message = {'source': 'ui', 'destination': 'enteties', 'operation': 'getUserData',
                   'data': {'number': number}}
    if inf == 'editinfo':
        id='1'
        name='gargoyle'
        email='asd@email'
        phone='911'
        message = {'source': 'ui','destination':'enteties','operation':'editUserInfo','data':{'userid':id,'name':name,'email':email,'phone':phone}}
    if inf == 'insertroom':
        description='pedro haha'
        number = '72'
        number_places = '50'
        message = {'source': 'ui','destination':'enteties','operation':'insertRoom','data':{'number':number,'description':description,'numberplaces':number_places}}
    if inf == 'access':
        userid = 13
        roomid = 3
        message = {'source': 'ui', 'destination': 'enteties', 'operation': 'checkAccess',
                   'data': {'userid':userid,'roomid':roomid}}
    if inf == 'getallrooms':
        message ={'source': 'ui', 'destination': 'enteties', 'operation': 'getAllRooms'}

    message = json.dumps(message)
    #message = '{"source":"ui" ,"destination":"entities" ,"operation": "registerTeacher", "data":{"name":'+str(name)+',"email":'+ str(email) +',"phone":'+str(phone)+',"number":'+str(number)+',"password":'+str(password)+'}}'
    message = message.encode('utf-8')
    # print("Mensagem enviada: ",message)
    client.send(message)
    #client.close()
    #print("socket closed")
    data = client.recv(max_size)
    if data:
        _data=data.decode('utf-8')
        print("Mensagem recebida: ",_data)
        _data = json.loads(_data)
        if _data['operation']=="access":
            print("Pode aceder: ",_data['data']['canAccess'])
        if _data['operation']=="book":
            print(_data)




