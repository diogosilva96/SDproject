import pika
import time


connection=pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='queue_server',durable=True) #fila persistente (durable)!

def buildMessage():
    print("Digite o id do utilizador e da sala no formato [userid,roomid]")
    urid=input()
    aList=urid.split(",")
    if len(aList) == 2:
      uid = int(aList[0])
      rid = int(aList[1])
      if int(uid) and int(rid):
          t = time.localtime()
          day = str(t.tm_mday)
          month = str(t.tm_mon)
          year = str(t.tm_year)
          th = str(t.tm_hour)
          tm = str(t.tm_min)
          ts = str(t.tm_sec)
          message = '{"source": 2 ,"destination": 3, "data":{"userid":' + str(uid) + ', "roomid":' + str(
              rid) + ',"day": ' + day + ' , "month":' + month + ', "year":' + year + ',"hours":' + th + ' ,"minutes":' + tm + ' ,"seconds":' + ts + '}}'
          message=message.encode('utf-8')
          #message=message.decode()
          #parsed_json = json.loads(message)
          #print(parsed_json)
          #print(parsed_json['data']['seconds'])
          return message
      else:
          print("Erro, insira 2 inteiros!")
          message = ""
          return message
    else:
        print("Erro, digite apenas 2 id's no formato [userid,roomid]")
        message = ""
        return message


print("Press CTRL+C + ENTER to exit")
while True:
    #key = ord(getch())
    #if key == 120: #120 = x
        #print("Sucessfully closed!")
        #break
    try:
        message = buildMessage()
        if message != "":
            channel.basic_publish(exchange='',routing_key='task_queue',body=message,properties=pika.BasicProperties(delivery_mode=2))#exchange='' equivale a default exchange
            print("[Card Reader]Sent: %r " %message)
        else:
            print("Erro os valores introduzidos não se encontram no formato!")
    except ValueError:
        print("Por favor digite 2 inteiros")
    except KeyboardInterrupt:
        print("Sucessfully exited!")
        break

connection.close()


