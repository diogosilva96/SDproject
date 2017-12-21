import pika
import time
import json


connection=pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='queue_server',durable=True) #fila persistente (durable)!

def buildMessage():
    print("[Card Reader] Please type de user id in the format [userid,roomid]")
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
          message = {'source':'cardreader','destination':'timetable','operation':'access','data':{'userid':str(uid),'roomid':str(rid),'day':day,'month':month,'year':year,'hours':th,'minutes':tm,'seconds':ts}}
          message=json.dumps(message)
          message=message.encode('utf-8')
          #message=message.decode()
          #parsed_json = json.loads(message)
          #print(parsed_json)
          #print(parsed_json['data']['seconds'])
          return message
      else:
          print("[Card Reader] Error, please type 2 integers!")
          message = ""
          return message
    else:
        print("[Card Reader] Error, please type only a userid and a roomid in the format [userid,roomid]")
        message = ""
        return message


print("[Card Reader] Press CTRL+C + ENTER to exit")
while True:
    #key = ord(getch())
    #if key == 120: #120 = x
        #print("Sucessfully closed!")
        #break
    try:
        message = buildMessage()
        if message != "":
            channel.basic_publish(exchange='',routing_key='queue_server',body=message,properties=pika.BasicProperties(delivery_mode=2))#exchange='' equivale a default exchange
            print("[Card Reader]Sent: %r " %message)
        else:
            print("[Card Reader] Error the inserted values are not in the correct format!")
    except ValueError:
        print("[Card Reader] Please type 2 integers in the format [userid,roomid]")
    except KeyboardInterrupt:
        print("[Card Reader] Sucessfully exited!")
        break

connection.close()


