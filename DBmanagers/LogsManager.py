import socket
import threading
from datetime import datetime
import pika
import mysql.connector

#DB CONNECTION #
conn = mysql.connector.connect(host="localhost",user='root', database='logs')
cursor = conn.cursor()


def insertLog(description):
    add_log = ("INSERT INTO logs "
                      "(description)"
                      "VALUES (%s)")
    cursor.execute(add_log, (description,))
    conn.commit()

connection=pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel=connection.channel()
channel.queue_declare(queue='queue_logs', durable=True)
print('[Logs Manager]Waiting for messages. Exit with ctrl+c')

def callback(ch,method,properties,body):
    message = body
    message = message.decode('utf-8')
    print("[Logs Manager] Message received: ",message)
    insertLog(message)
    print("[Logs Manager] Log was inserted in database.")
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,queue='queue_logs')

channel.start_consuming()

