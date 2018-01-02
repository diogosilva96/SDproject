from datetime import datetime
from threading import Thread
import socket
import json
import pika
import time

# address = ('192.168.2.101', 8000)
# addressEnteties = ('192.168.2.101', 8001)
# addressSchedules = ('192.168.2.101', 8002)
# addressLogs = ('192.168.2.101', 8003)
# addressConsoleLogs = ('192.168.1.102', 8002)
address = ('localhost', 8000)
addressEnteties = ('localhost', 8001)
addressSchedules = ('localhost', 8002)
addressLogs = ('localhost', 8003)
addressConsoleLogs = ('localhost', 8004)

print('[SystemMediator] Starting the server at ', datetime.now())

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

enteties = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
schedules = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
logs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
consoleLogs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

enteties.connect(addressEnteties)
schedules.connect(addressSchedules)
logs.connect(addressLogs)
consoleLogs.connect(addressConsoleLogs)

#########################################################################################

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='queue_server', durable=True)
print('[SystemMediator] waiting for messages. Exit with CTRL+C')


def callback(ch, method, properties, body):
    print(body)
    enteties.send(body)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print('[SystemMediator] Message sent to enteties at', datetime.now())
    thread = AcessAnalyzer(body)
    thread.start()


class Consumer(Thread):
    def __init__(self, channel):
        Thread.__init__(self)
        self.channel = channel

    def run(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(callback, queue='queue_server')
        self.channel.start_consuming()


class AcessAnalyzer(Thread):
    def __init__(self, body):
        Thread.__init__(self)
        self.body = body

    def run(self):
        temp = enteties.recv(max_size)
        temp = to_json(temp)
        print('[SystemMediator] Message received from enteties at', datetime.now())
        if temp['result'] != "denied":
            temp = to_bits(temp)
            consoleLogs.send(temp)
            print('[SystemMediator] Message sent to consoleLogs at', datetime.now())
        else:
            schedules.send(self.body)
            print('[SystemMediator] Message sent to timetables at', datetime.now())
            temp = schedules.recv(max_size)
            print('[SystemMediator] Message received from schedules at', datetime.now())
            consoleLogs.send(temp)
            print('[SystemMediator] Message sent to consoleLogs at', datetime.now())

#########################################################################################


class Receiver(Thread):
    def __init__(self, client_connection, client_address):
        Thread.__init__(self)
        self.client = client_connection
        self.address = client_address

    def run(self):
        while True:
            pm_data = self.client.recv(max_size)
            print('[SystemMediator] Message received from client of connection at', datetime.now())
            pm_thread_analyzer = RequestAnalyzer(pm_data, self.client, self.address)
            pm_thread_analyzer.start()


def to_bits(data):
    data = json.dumps(data)
    return data.encode('utf-8')


def to_json(data):
    data = data.decode('utf-8')
    return json.loads(data)


class RequestAnalyzer(Thread):
    def __init__(self, data, client_connection, client_address):
        Thread.__init__(self)
        self.client = client_connection
        self.address = client_address
        self.data = to_json(data)

    def run(self):
        pm_temp_data = to_bits(self.data)
        if self.data['destination'] == "enteties":
            enteties.send(pm_temp_data)
            print('[SystemMediator] Message sent to enteties at', datetime.now())
            data = enteties.recv(max_size)
            print('[SystemMediator] Message received from enteties at', datetime.now())
            pm_data = to_json(data)
            if 'result' in pm_data:
                if pm_data['result'] == "denied" and pm_data["operation"] == "access":
                    pm_temp_data = to_bits(pm_data)
                    schedules.send(pm_temp_data)
                    print('[SystemMediator] Message sent to timetables at', datetime.now())
                    data = schedules.recv(max_size)
                    print('[SystemMediator] Message received from timetables at', datetime.now())
                    if self.address[1] == 6790:
                        self.client.send(data)
                        print('[SystemMediator] Message sent to client of connection at', datetime.now())
                        logs.send(data)
                        print('[SystemMediator] Message sent to logs at', datetime.now())

                else:
                    self.client.send(data)
                    print('[SystemMediator] Message sent to client of connection at', datetime.now())
                    logs.send(data)
                    print('[SystemMediator] Message sent to logs at', datetime.now())
            else:
                self.client.send(data)
                logs.send(data)
                print('[SystemMediator] Message sent to logs at', datetime.now())

        elif self.data['destination'] == "timetables":
            schedules.send(pm_temp_data)
            print('[SystemMediator] Message sent to timetables at', datetime.now())
            data = schedules.recv(max_size)
            print('[SystemMediator] Message received from timetables at', datetime.now())
            self.client.send(data)
            print('[SystemMediator] Message sent to client of connection at', datetime.now())
            logs.send(data)
            print('[SystemMediator] Message sent to logs at', datetime.now())
        else:
            print("[SystemMediator] Some error occoured because the messages didnt have a field with destination defined")


if __name__ == "__main__":
    max_size = 1000
################################################
    consumer = Consumer(channel)
    consumer.start()
###############################################
    connections = 2
    server.bind(address)
    server.listen(3)
    while connections != 0:
        client, addr = server.accept()
        connections -= 1
        NewConnection = Receiver(client, addr)
        NewConnection.start()
    while True:
        pass
