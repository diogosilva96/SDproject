from datetime import datetime
from threading import Thread
import socket
import json


class RequestAnalyzer(Thread):
    def __init__(self, data):
        Thread.__init__(self)
        self.data = data

    def run(self):
        if 'destination' in self.data:
            pm_temp_data = self.data['data']
            pm_temp_data = json.dumps(pm_temp_data)
            pm_temp_data = pm_temp_data.encode('utf-8')
            if self.data['destination'] == "enteties":
                enteties.send(pm_temp_data)
            elif self.data['destination'] == "schedule":
                schedules.send(pm_temp_data)
            elif self.data['destination'] == "log":
                logs.send(pm_temp_data)
            else:
                print("Some error occour because in the messages didnt had a field with destination defined")
        elif 'source' in self.data:
            pm_temp_data = json.dumps(self.data)
            pm_temp_data = pm_temp_data.encode('utf-8')
            if self.data['source'] == "enteties":
                # send UI and console and logs
                UI.send(pm_temp_data)
                console.send(pm_temp_data)
                logs.send(pm_temp_data)
            elif self.data['source'] == "schedule":
                # send UI and console and logs
                UI.send(pm_temp_data)
                console.send(pm_temp_data)
                logs.send(pm_temp_data)
            else:
                print("Some error occour because in the messages didnt had a field with source defined")
        else:
            print("Some error occour because in the messages didnt had a field with destination or source")


if __name__ == "__main__":
    max_size = 1000

    address = ('192.168.1.6', 6789)
    addressEnteties = ('192.168.1.6', 8000)
    addressSchedules = ('192.168.1.6', 8001)
    addressLogs = ('192.168.1.6', 8002)
    addressUI = ('192.168.1.4', 6789)
    addressConsole = ('192.168.1.4', 6790)

    print('Starting the server at ', datetime.now())
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    enteties = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    schedules = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    UI = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    console = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    """
    Falta fazer os web sockets
    """
    enteties.connect(addressEnteties)
    schedules.connect(addressSchedules)
    logs.connect(addressLogs)
    UI.connect(addressUI)
    console.connect(console)

    server.bind(address)
    server.listen(5)
    client, addr = server.accept()
    while True:
        pm_data = client.recv(max_size)
        pm_data = pm_data.decode('utf-8')
        pm_data = json.loads(pm_data)
        pm_thread_analyzer = RequestAnalyzer(pm_data)
        pm_thread_analyzer.start()
        """
            Starts a threads to analyze the request and the main idea
             is to start different thread from the first one, and after
              that do it with lcoks!!
        """
