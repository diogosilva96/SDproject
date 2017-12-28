from datetime import datetime
from threading import Thread
import socket
import json
import pika

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

print('Starting the server at ', datetime.now())

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

enteties = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
schedules = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
logs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# consoleLogs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

enteties.connect(addressEnteties)
schedules.connect(addressSchedules)
logs.connect(addressLogs)
# consoleLogs.connect(addressConsoleLogs)


def callback(ch,method,properties,body):
    ch.basic_ack(delivery_tag=method.delivery_tag)
    enteties.send(body)
    temp = enteties.recv(max_size)
    if temp['result'] != "denied":
        temp = to_json(temp)
        # consoleLogs.send(temp)
    else:
        schedules.send(body)
        temp = schedules.recv(max_size)
        # consoleLogs.send(temp)


class Receiver(Thread):
    def __init__(self, client_connection, client_address):
        Thread.__init__(self)
        self.client = client_connection
        self.address = client_address

    def run(self):
        while True:
            pm_data = self.client.recv(max_size)
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
            data = enteties.recv(max_size)
            pm_data = to_json(data)
            if 'result' in pm_data:
                if pm_data['result'] == "denied" and pm_data["operation"] == "access":
                    schedules.send(pm_temp_data)
                    data = schedules.recv(max_size)
                    if self.address[1] == 6790:
                        self.client.send(data)
                        logs.send(data)
                else:
                    self.client.send(data)
                    logs.send(data)
            else:
                self.client.send(data)
                logs.send(data)
        elif self.data['destination'] == "timetables":
            schedules.send(pm_temp_data)
            data = schedules.recv(max_size)
            self.client.send(data)
            logs.send(data)
        else:
            print("Some error occoured because the messages didnt have a field with destination defined")


if __name__ == "__main__":
    max_size = 1000

    #connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    #channel = connection.channel()
    #channel.queue_declare(queue='queue_server')
    #channel.basic_consume(callback, queue='hello', durable=True)
    #print('[*] waiting for messages. Exit with CTRL+C')
    #channel.start_consuming()

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
